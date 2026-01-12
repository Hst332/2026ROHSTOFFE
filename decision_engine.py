def decide(asset, score):
    if asset == "GOLD":
        if score >= 0.55:
            return "LONG_FULL"
        elif score >= 0.53:
            return "LONG_HALF"
        else:
            return "NO_TRADE"

    if asset == "SILVER":
        if score >= 0.96:
            return "LONG"
        else:
            return "NO_TRADE"

    if asset == "COPPER":
        if score >= 0.56:
            return "LONG"
        else:
            return "NO_TRADE"

    if asset == "NATURAL GAS":
        if score >= 0.56:
            return "LONG"
        elif score <= 0.44:
            return "SHORT"
        else:
            return "NO_TRADE"

    return "NO_TRADE"
