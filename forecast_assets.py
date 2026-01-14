import yfinance as yf

from model_core import model_score
from forecast_utils import forecast_trend
from decision_engine import decide


# --------------------------------------------------
# ASSET DEFINITIONS (fix & explizit)
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
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    # Last close
    close = round(float(df["Close"].iloc[-1]), 1)

    # Core model score
    score = model_score(df)

    # Trend forecasts
    f_1_5 = forecast_trend(df, days=5)
    f_2_3 = forecast_trend(df, days=15)

    # Aggregate main signal
    if f_1_5 == "++" and f_2_3 == "++":
        signal = "LONG"
    elif f_1_5 == "--" and f_2_3 == "--":
        signal = "SHORT"
    else:
        signal = "NO_TRADE"

    # ChatGPT overlay / decision engine
    decision = decide(
        asset=asset,
        score=score,
        signal=signal,
        signal_1_5d=f_1_5,
        signal_2_3w=f_2_3,
        macro_bias=macro_bias
    )

    return {
        "asset": asset,
        "close": close,
        "score": score,
        "signal": signal,
        "f_1_5": f_1_5,
        "f_2_3": f_2_3,
        "gpt_1_5d": decision["gpt_1_5d"],
        "gpt_2_3w": decision["gpt_2_3w"],
        "final": decision["final"],
    }


# --------------------------------------------------
# RUN ALL ASSETS
# --------------------------------------------------

def run_all():
    results = []

    for asset, ticker, macro_bias in ASSETS:
        results.append(
            forecast_asset(asset, ticker, macro_bias)
        )

    return results
