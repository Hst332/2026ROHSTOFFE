# forecast_utils.py

def forecast_trend(df, days):
    last = float(df["Close"].iloc[-1])
    past = float(df["Close"].iloc[-days])
    r = (last - past) / past

    if r > 0.01:
        return "++"
    elif r < -0.01:
        return "--"
    else:
        return "+"
