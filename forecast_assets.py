import yfinance as yf
import pandas as pd

from model_core import model_score
from forecast_utils import forecast_trend
from decision_engine import decide
from signal_guard import guard_dataframe


def _normalize_yfinance_df(df: pd.DataFrame) -> pd.DataFrame:
    """Make yfinance output compatible with the rest of the code.

    Newer yfinance/pandas combos can return MultiIndex columns like:
        ('Close','GC=F')
    which breaks code expecting a simple 'Close' Series.
    We collapse MultiIndex to the first level and, if duplicates exist,
    keep the first column for each OHLCV field.
    """
    if df is None:
        return df

    if isinstance(df.columns, pd.MultiIndex):
        # Keep level 0 (Open/High/Low/Close/Volume/Adj Close)
        df = df.copy()
        df.columns = [c[0] if isinstance(c, tuple) else c for c in df.columns]
        # If we now have duplicate columns, keep the first occurrence
        if df.columns.duplicated().any():
            df = df.loc[:, ~df.columns.duplicated()]
    return df


def _last_scalar_from_df(df: pd.DataFrame, col: str):
    if df is None or len(df) == 0 or col not in df.columns:
        return None
    v = df[col].iloc[-1]
    # If MultiIndex collapse failed, v might still be a Series
    if isinstance(v, pd.Series):
        if len(v) == 0:
            return None
        v = v.iloc[0]
    try:
        return v.item() if hasattr(v, "item") else float(v)
    except Exception:
        try:
            return float(v)
        except Exception:
            return None


# --------------------------------------------------
# ASSET DEFINITIONS
# --------------------------------------------------

ASSETS = [
    ("GOLD", "GC=F", "STRONG_SUPPORT"),
    ("SILVER", "SI=F", "NO_SUPPORT"),
    ("NATURAL GAS", "NG=F", "STRONG_SUPPORT"),
    ("COPPER", "HG=F", "STRONG_SUPPORT"),
]


# --------------------------------------------------
# SINGLE ASSET FORECAST
# --------------------------------------------------

def forecast_asset(asset, ticker, macro_bias):
    # NOTE:
    # If you switch to intraday (e.g. interval="1m"), the guard will automatically
    # infer the bar timeframe from the index and block stale/NaN data.
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)
    df = _normalize_yfinance_df(df)

    # Hard fail-safe: do NOT compute signals on empty data
    guard = guard_dataframe(
        asset=asset,
        df=df,
        # Volume is not reliably present for all futures symbols on Yahoo.
        required_cols=("Open", "High", "Low", "Close"),
        critical_last_cols=("Close",),
        min_rows=30,
        timeframe_seconds=None,      # auto-infer
        max_stale_multiplier=2,
        assume_index_is_utc=True
    )

    # If data is unusable: return a blocked result instead of crashing the whole run
    if not guard.data_ok:
        close = _last_scalar_from_df(df, "Close")
        return {
            "asset": asset,
            "close": round(close, 1) if close is not None else None,
            "score": 0.0,
            "signal": "NO_TRADE",
            "f_1_5": 0.0,
            "f_2_3": 0.0,
            "gpt_1_5d": "NA",
            "gpt_2_3w": "NA",
            "final": "NO_TRADE(DATA)",
            "zusatzinfo": f"DATA BLOCK: {guard.reason}",
            "data_ok": guard.data_ok,
            "last_bar_utc": guard.last_bar_utc,
            "age_s": guard.age_s,
            "rows": guard.rows,
            "nan_last": guard.nan_last,
            "stale": guard.stale,
            "timeframe_s": guard.timeframe_s,
            "guard_reason": guard.reason,
        }

    # Existing pipeline
    close_val = _last_scalar_from_df(df, "Close")
    close = round(close_val, 1) if close_val is not None else None

    score = model_score(df)

    f_1_5 = forecast_trend(df, days=5)
    f_2_3 = forecast_trend(df, days=15)

    # ---- MINI BACKTEST LOG ----
    print(
        f"{asset:<10} | SCORE={score:.3f} | "
        f"1-5D={f_1_5:+.3f} | 2-3W={f_2_3:+.3f} | "
        f"DATA_OK={guard.data_ok} AGE_s={guard.age_s}"
    )

    decision = decide(
        asset=asset,
        score=score,
        signal_1_5d=f_1_5,
        signal_2_3w=f_2_3,
        macro_bias=macro_bias
    )

    return {
        "asset": asset,
        "close": close,
        "score": score,
        "signal": decision["rule_signal"],   # nur Regelstatus
        "f_1_5": f_1_5,
        "f_2_3": f_2_3,
        "gpt_1_5d": decision["gpt_1_5d"],
        "gpt_2_3w": decision["gpt_2_3w"],
        "final": decision["action"],         # echte Handlung
        "zusatzinfo": decision["zusatzinfo"],

        # Guard fields (so du siehst sofort, ob du dem Signal trauen kannst)
        "data_ok": guard.data_ok,
        "last_bar_utc": guard.last_bar_utc,
        "age_s": guard.age_s,
        "rows": guard.rows,
        "nan_last": guard.nan_last,
        "stale": guard.stale,
        "timeframe_s": guard.timeframe_s,
        "guard_reason": guard.reason,
    }


# --------------------------------------------------
# RUN ALL ASSETS
# --------------------------------------------------

def run_all():
    results = []

    for asset, ticker, macro_bias in ASSETS:
        try:
            results.append(
                forecast_asset(asset, ticker, macro_bias)
            )
        except Exception as e:
            # Never crash the whole run for one asset
            results.append({
                "asset": asset,
                "close": None,
                "score": 0.0,
                "signal": "NO_TRADE",
                "f_1_5": 0.0,
                "f_2_3": 0.0,
                "gpt_1_5d": "NA",
                "gpt_2_3w": "NA",
                "final": "NO_TRADE(ERROR)",
                "zusatzinfo": f"ERROR: {type(e).__name__}: {e}",

                "data_ok": False,
                "last_bar_utc": "NA",
                "age_s": 10**9,
                "rows": 0,
                "nan_last": 1,
                "stale": 1,
                "timeframe_s": 0,
                "guard_reason": f"ERROR: {type(e).__name__}",
            })

    return results
