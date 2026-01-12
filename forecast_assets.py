import yfinance as yf
from model_core import model_score
from forecast_utils import forecast_trend
from decision_engine import decide

ASSETS = [
    ("GOLD", "GC=F", "USD/oz"),
    ("SILVER", "SI=F", "USD/oz"),
    ("NATURAL GAS", "NG=F", "USD/MMBtu"),
    ("COPPER", "HG=F", "USD/lb"),
]

def forecast_asset(name, ticker, unit):
    df = yf.download(ticker, period="1y", interval="1d", progress=False)

    close = round(float(df["Close"].iloc[-1]), 1)
    score = round(model_score(df), 3)
    signal = decide(name, score)

    return {
        "asset": name,
        "close": close,
        "unit": unit,
        "score": score,
        "signal": signal,
        "f_1_5": forecast_trend(df, 5),
        "f_2_3": forecast_trend(df, 21),
    }

def run_all():
    return [forecast_asset(*a) for a in ASSETS]
