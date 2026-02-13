"""
print_with_guard.py

Drop-in Ersatz für deine bestehende Tabelle:
- Behält deine Spalten (ASSET, CLOSE, SCORE, SIGNAL, 1-5D, 2-3W, GPT 1-5D, GPT 2-3W, FINAL, ZUSATZINFO)
- Ergänzt DATA_OK + LAST_BAR + AGE_s + NAN_LAST + STALE
- Erzwingt: FINAL = NO_TRADE(DATA) wenn Daten nicht ok
"""

from dataclasses import dataclass
from datetime import datetime, timezone
import pandas as pd


# -----------------------------
# Guard
# -----------------------------

@dataclass
class GuardResult:
    data_ok: bool
    last_bar: str
    age_s: int
    rows: int
    nan_last: int
    stale: int
    reason: str


def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def guard_intraday_df(
    df: pd.DataFrame,
    *,
    timeframe_seconds: int = 60,
    max_stale_multiplier: int = 2,
    min_rows: int = 200,
    required_cols=("Open", "High", "Low", "Close", "Volume"),
    critical_last_cols=("Close", "Volume"),
    assume_index_is_utc: bool = True,
) -> GuardResult:
    reasons = []
    data_ok = True

    if df is None or len(df) == 0:
        return GuardResult(False, "NA", 10**9, 0, 1, 1, "EMPTY_DF")

    rows = len(df)

    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        data_ok = False
        reasons.append("MISSING_COLS:" + ",".join(missing))

    if rows < min_rows:
        data_ok = False
        reasons.append("HISTORY_SHORT")

    try:
        last_bar_dt = df.index[-1]
        if isinstance(last_bar_dt, pd.Timestamp):
            last_bar_dt = last_bar_dt.to_pydatetime()
    except Exception:
        return GuardResult(False, "NA", 10**9, rows, 1, 1, "BAD_INDEX")

    now_utc = datetime.now(timezone.utc)

    if last_bar_dt.tzinfo is None:
        if assume_index_is_utc:
            last_bar_dt = last_bar_dt.replace(tzinfo=timezone.utc)
        else:
            last_bar_dt = last_bar_dt.replace(tzinfo=timezone.utc)

    age_s = _safe_int((now_utc - last_bar_dt).total_seconds(), 10**9)
    max_stale_seconds = timeframe_seconds * max_stale_multiplier
    stale = 1 if age_s > max_stale_seconds else 0
    if stale:
        data_ok = False
        reasons.append("STALE_DATA")

    last_bar_str = last_bar_dt.astimezone().strftime("%Y-%m-%d %H:%M:%S")

    nan_last = 0
    for c in critical_last_cols:
        if c in df.columns and pd.isna(df[c].iloc[-1]):
            nan_last = 1
            break
    if nan_last:
        data_ok = False
        reasons.append("NAN_LAST_ROW")

    reason = "OK" if data_ok else ";".join(reasons)
    return GuardResult(data_ok, last_bar_str, age_s, rows, nan_last, stale, reason)


# -----------------------------
# Row = genau deine Tabelle
# -----------------------------

@dataclass
class SignalRow:
    asset: str
    close: float
    score: float
    signal: str
    d1_5: float
    w2_3: float
    gpt_1_5d: str
    gpt_2_3w: str
    final: str
    zusatzinfo: str


def print_table_with_guard(
    rows: list[SignalRow],
    df_map: dict[str, pd.DataFrame],
    *,
    timeframe_seconds: int = 60,
    max_stale_multiplier: int = 2,
    min_rows: int = 200,
    required_cols=("Open", "High", "Low", "Close", "Volume"),
    critical_last_cols=("Close", "Volume"),
    assume_index_is_utc: bool = True,
):
    runtime_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    print(f"Run time (UTC): {runtime_utc}")
    print("=" * 170)
    print(
        "ASSET         CLOSE     SCORE   SIGNAL       1-5D      2-3W      GPT 1-5D   GPT 2-3W   "
        "FINAL           DATA_OK  LAST_BAR            AGE_s  NAN_LAST  STALE  ZUSATZINFO"
    )
    print("-" * 170)

    for r in rows:
        df = df_map.get(r.asset)
        g = guard_intraday_df(
            df,
            timeframe_seconds=timeframe_seconds,
            max_stale_multiplier=max_stale_multiplier,
            min_rows=min_rows,
            required_cols=required_cols,
            critical_last_cols=critical_last_cols,
            assume_index_is_utc=assume_index_is_utc,
        )

        final_for_trade = r.final if g.data_ok else "NO_TRADE(DATA)"

        print(
            f"{r.asset:<12}  "
            f"{r.close:>7.1f}  "
            f"{r.score:>7.3f}  "
            f"{r.signal:<9}  "
            f"{r.d1_5:>8.4f}  "
            f"{r.w2_3:>8.4f}  "
            f"{r.gpt_1_5d:<9}  "
            f"{r.gpt_2_3w:<9}  "
            f"{final_for_trade:<14}  "
            f"{str(g.data_ok):<6}  "
            f"{g.last_bar:<19}  "
            f"{g.age_s:>5}  "
            f"{g.nan_last:>8}  "
            f"{g.stale:>5}  "
            f"{r.zusatzinfo}"
        )

        if not g.data_ok:
            print(f"{'':<12}  >>> BLOCKED: {g.reason}")

    print("=" * 170)
