from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Tuple, Dict, Any

import pandas as pd


@dataclass
class GuardResult:
    asset: str
    data_ok: bool
    last_bar_utc_raw: str          # always full UTC timestamp string
    last_bar_utc_display: str      # pretty display (date-only if 00:00:00)
    age_s: int
    age_h: float
    rows: int
    nan_last: int
    stale: int
    timeframe_s: int
    reason: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _safe_int(x, default: int = 0) -> int:
    try:
        return int(x)
    except Exception:
        return default


def infer_timeframe_seconds(index: pd.Index, *, fallback_seconds: int = 86400) -> int:
    """Infer bar timeframe from a DateTimeIndex (median delta of last ~50 points)."""
    try:
        if not isinstance(index, pd.DatetimeIndex):
            return fallback_seconds
        if len(index) < 3:
            return fallback_seconds

        n = min(len(index), 50)
        idx = index[-n:]
        deltas = (idx[1:] - idx[:-1]).to_series().dt.total_seconds().dropna()
        if deltas.empty:
            return fallback_seconds

        tf = int(round(float(deltas.median())))
        if tf <= 0:
            return fallback_seconds

        return max(1, min(tf, 7 * 86400))
    except Exception:
        return fallback_seconds


def _last_scalar(df: pd.DataFrame, col: str):
    """Return a scalar from the last row for col, even if it is a Series (MultiIndex edge cases)."""
    try:
        v = df[col].iloc[-1]
        if isinstance(v, pd.Series):
            # pick first non-null if available, else first
            vn = v.dropna()
            v = vn.iloc[0] if len(vn) > 0 else v.iloc[0]
        return v
    except Exception:
        return None


def _format_last_bar_display(dt_utc: datetime) -> str:
    """
    If the time is 00:00:00 -> display only date.
    Else -> display YYYY-MM-DD HH:MM (no seconds).
    """
    if dt_utc.hour == 0 and dt_utc.minute == 0 and dt_utc.second == 0:
        return dt_utc.strftime("%Y-%m-%d")
    return dt_utc.strftime("%Y-%m-%d %H:%M")


def guard_dataframe(
    asset: str,
    df: Optional[pd.DataFrame],
    *,
    now_utc: Optional[datetime] = None,
    required_cols: Tuple[str, ...] = ("Open", "High", "Low", "Close"),
    critical_last_cols: Tuple[str, ...] = ("Close",),
    min_rows: int = 30,
    timeframe_seconds: Optional[int] = None,
    max_stale_multiplier: int = 2,
    assume_index_is_utc: bool = True,
) -> GuardResult:

    if now_utc is None:
        now_utc = datetime.now(timezone.utc)

    if df is None or len(df) == 0:
        return GuardResult(
            asset=asset,
            data_ok=False,
            last_bar_utc_raw="NA",
            last_bar_utc_display="NA",
            age_s=10**9,
            age_h=float(10**9) / 3600.0,
            rows=0,
            nan_last=1,
            stale=1,
            timeframe_s=_safe_int(timeframe_seconds, 0),
            reason="EMPTY_DF",
        )

    rows = len(df)
    reasons = []
    data_ok = True

    # columns
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        data_ok = False
        reasons.append("MISSING_COLS:" + ",".join(missing))

    if rows < min_rows:
        data_ok = False
        reasons.append("HISTORY_SHORT")

    # last bar timestamp
    try:
        last_bar = df.index[-1]
        if isinstance(last_bar, pd.Timestamp):
            last_bar = last_bar.to_pydatetime()
    except Exception:
        return GuardResult(
            asset=asset,
            data_ok=False,
            last_bar_utc_raw="NA",
            last_bar_utc_display="NA",
            age_s=10**9,
            age_h=float(10**9) / 3600.0,
            rows=rows,
            nan_last=1,
            stale=1,
            timeframe_s=_safe_int(timeframe_seconds, 0),
            reason="BAD_INDEX",
        )

    if getattr(last_bar, "tzinfo", None) is None:
        if assume_index_is_utc:
            last_bar = last_bar.replace(tzinfo=timezone.utc)
        else:
            last_bar = last_bar.replace(tzinfo=timezone.utc)

    last_bar_utc = last_bar.astimezone(timezone.utc)

    # timeframe inference
    tf = timeframe_seconds if timeframe_seconds is not None else infer_timeframe_seconds(df.index)
    tf = _safe_int(tf, 0)
    if tf <= 0:
        tf = 86400

    age_s = _safe_int((now_utc - last_bar_utc).total_seconds(), 10**9)
    age_h = round(age_s / 3600.0, 2)

    max_stale_s = tf * max_stale_multiplier
    stale = 1 if age_s > max_stale_s else 0
    if stale:
        data_ok = False
        reasons.append("STALE_DATA")

    # NaN last row in critical columns
    nan_last = 0
    for c in critical_last_cols:
        v = _last_scalar(df, c) if c in df.columns else None
        if v is None or pd.isna(v):
            nan_last = 1
            break
    if nan_last:
        data_ok = False
        reasons.append("NAN_LAST_ROW")

    raw_ts = last_bar_utc.strftime("%Y-%m-%d %H:%M:%S")
    disp_ts = _format_last_bar_display(last_bar_utc)

    return GuardResult(
        asset=asset,
        data_ok=data_ok,
        last_bar_utc_raw=raw_ts,
        last_bar_utc_display=disp_ts,
        age_s=age_s,
        age_h=age_h,
        rows=rows,
        nan_last=nan_last,
        stale=stale,
        timeframe_s=tf,
        reason="OK" if data_ok else ";".join(reasons),
    )
