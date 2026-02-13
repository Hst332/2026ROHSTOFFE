"""
signal_guard.py

Robuster Intraday Signal-Guard für manuelles Trading.
Erzwingt:
- Kein Trade bei fehlerhaften Daten
- Stale-Data Erkennung
- NaN-Prüfung
- Historienprüfung
- Sauberes, sofort sichtbares Output-Format
- Optional JSONL Logging

Verwendung:
    from signal_guard import (
        audit_and_format_signal,
        print_audit_header,
        print_audit_row,
        append_audit_jsonl
    )
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
import json
import sys


# ==========================================================
# DATA STRUCTURE
# ==========================================================

@dataclass
class SignalAudit:
    time_local: str
    asset: str
    data_ok: bool
    last_bar: str
    age_s: int
    rows: int
    nan_last: int
    stale: int
    history_short: int
    signal_raw: str
    signal_trade: str
    reason: str


# ==========================================================
# INTERNAL HELPERS
# ==========================================================

def _safe_int(x, default=0):
    try:
        return int(x)
    except Exception:
        return default


def _color(text, color_code):
    if sys.stdout.isatty():
        return f"\033[{color_code}m{text}\033[0m"
    return text


# ==========================================================
# CORE GUARD FUNCTION
# ==========================================================

def audit_and_format_signal(
    asset: str,
    df: pd.DataFrame,
    signal_raw: str,
    *,
    timeframe_seconds: int = 60,          # 1m default
    max_stale_multiplier: int = 2,        # stale wenn > timeframe * multiplier
    min_rows: int = 200,
    required_cols: tuple = ("Open", "High", "Low", "Close", "Volume"),
    critical_last_cols: tuple = ("Close", "Volume"),
    assume_index_is_utc: bool = True
) -> SignalAudit:

    reasons = []
    data_ok = True
    history_short_flag = 0

    # ------------------------------------------------------
    # Basic Data Checks
    # ------------------------------------------------------

    if df is None or len(df) == 0:
        data_ok = False
        reasons.append("EMPTY_DF")
        last_bar_dt = None
        rows = 0
    else:
        rows = len(df)

        # Required columns
        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            data_ok = False
            reasons.append("MISSING_COLS:" + ",".join(missing))

        # Minimum history
        if rows < min_rows:
            data_ok = False
            history_short_flag = 1
            reasons.append("HISTORY_SHORT")

        # Last timestamp
        try:
            last_bar_dt = df.index[-1]
            if isinstance(last_bar_dt, pd.Timestamp):
                last_bar_dt = last_bar_dt.to_pydatetime()
        except Exception:
            last_bar_dt = None
            data_ok = False
            reasons.append("BAD_INDEX")

    # ------------------------------------------------------
    # Stale Data Check (INTRADAY CRITICAL)
    # ------------------------------------------------------

    now_utc = datetime.now(timezone.utc)

    if last_bar_dt is None:
        age_s = 10**9
        stale = 1
        data_ok = False
        reasons.append("NO_LAST_BAR")
        last_bar_str = "NA"
    else:
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

    # ------------------------------------------------------
    # NaN Check on Last Row
    # ------------------------------------------------------

    nan_last = 0

    if df is None or len(df) == 0:
        nan_last = 1
    else:
        for c in critical_last_cols:
            if c in df.columns:
                if pd.isna(df[c].iloc[-1]):
                    nan_last = 1
                    break

        if nan_last:
            data_ok = False
            reasons.append("NAN_LAST_ROW")

    # ------------------------------------------------------
    # Final Signal Enforcement
    # ------------------------------------------------------

    signal_trade = signal_raw if data_ok else "NO_TRADE(DATA)"
    reason = "OK" if data_ok else ";".join(reasons)

    return SignalAudit(
        time_local=datetime.now().astimezone().strftime("%H:%M:%S"),
        asset=asset,
        data_ok=data_ok,
        last_bar=last_bar_str,
        age_s=age_s,
        rows=rows,
        nan_last=nan_last,
        stale=stale,
        history_short=history_short_flag,
        signal_raw=str(signal_raw),
        signal_trade=signal_trade,
        reason=reason
    )


# ==========================================================
# OUTPUT
# ==========================================================

def print_audit_header():
    print(
        "TIME      ASSET   DATA_OK  LAST_BAR            AGE_s  ROWS  "
        "NAN_LAST  STALE  HIST_SHORT  SIGNAL_RAW  SIGNAL_TRADE      REASON"
    )


def print_audit_row(a: SignalAudit):

    data_ok_col = _color(str(a.data_ok), "32") if a.data_ok else _color(str(a.data_ok), "31")
    signal_col = _color(a.signal_trade, "32") if a.data_ok else _color(a.signal_trade, "31")

    print(
        f"{a.time_local:<8}  "
        f"{a.asset:<7}  "
        f"{data_ok_col:<7}  "
        f"{a.last_bar:<19}  "
        f"{a.age_s:>5}  "
        f"{a.rows:>5}  "
        f"{a.nan_last:>8}  "
        f"{a.stale:>6}  "
        f"{a.history_short:>10}  "
        f"{a.signal_raw:<10}  "
        f"{signal_col:<15}  "
        f"{a.reason}"
    )


# ==========================================================
# LOGGING (OPTIONAL)
# ==========================================================

def append_audit_jsonl(audit: SignalAudit, path="signal_audit.jsonl"):
    p = Path(path)
    if not p.exists():
        p.write_text("", encoding="utf-8")

    with open(p, "a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(audit), ensure_ascii=False) + "\n")


# ==========================================================
# EXAMPLE USAGE
# ==========================================================

if __name__ == "__main__":
    # Demo DataFrame (Simuliert Intraday)
    import numpy as np

    now = datetime.now(timezone.utc)
    index = pd.date_range(end=now, periods=250, freq="1min")

    df_demo = pd.DataFrame({
        "Open": np.random.random(250),
        "High": np.random.random(250),
        "Low": np.random.random(250),
        "Close": np.random.random(250),
        "Volume": np.random.randint(100, 1000, 250)
    }, index=index)

    signal_raw = "BUY"

    print_audit_header()

    audit = audit_and_format_signal(
        asset="GOLD",
        df=df_demo,
        signal_raw=signal_raw,
        timeframe_seconds=60,
        max_stale_multiplier=2,
        min_rows=200
    )

    print_audit_row(audit)

    append_audit_jsonl(audit)
