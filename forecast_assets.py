import yfinance as yf
from model_core import model_score
from forecast_utils import forecast_trend
from decision_engine import decide

def forecast_asset(asset, df, macro_bias):
    close = round(float(df["Close"].iloc[-1]), 1)
    score = get_score(df)
    signal, f_1_5, f_2_3 = get_signal(df)

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
def run_all():
    results = []

    for asset, df, macro_bias in ASSETS:
        results.append(forecast_asset(asset, df, macro_bias))

    return results
