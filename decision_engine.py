from chatgpt_overlay import chatgpt_overlay

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

    gpt_1_5d, gpt_2_3w, final = chatgpt_overlay(
        asset=asset,
        signal_1_5d=signal_1_5d,
        signal_2_3w=signal_2_3w,
        macro=macro_bias
    )

