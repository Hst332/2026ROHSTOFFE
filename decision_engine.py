# decision_engine.py

def decide(asset, score):
    """
    Zentrale, backtest-konsistente Entscheidungslogik
    score = prob_up (0.0 – 1.0)
    """

    # GOLD
    if asset == "GOLD":
        if score >= 0.55:
            return "LONG_FULL"
        elif score >= 0.53:
            return "LONG_HALF"
        else:
            return "NO_TRADE"

    # SILVER
    if asset == "SILVER":
        if score >= 0.96:
            return "LONG"
        else:
            return "NO_TRADE"

    # COPPER
    if asset == "COPPER":
        if score >= 0.56:
            return "LONG"
        else:
            return "NO_TRADE"

    # NATURAL GAS
    if asset == "NATURAL GAS":
        if score >= 0.56:
            return "LONG"
        elif score <= 0.44:
            return "SHORT"
        else:
            return "NO_TRADE"

    return "NO_TRADE"
