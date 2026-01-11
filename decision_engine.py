# decision_engine.py

def decide(asset: str, score: float):
    """
    Zentrale Entscheidungslogik.
    Gibt (signal, explanation) zurück.
    """

    # GOLD --------------------------------------------------
    if asset == "GOLD":
        if score >= 0.55:
            return "LONG_FULL", "score >= 0.55 → 100 % Long"
        elif score >= 0.53:
            return "LONG_HALF", "0.53 ≤ score < 0.55 → 50 % Long"
        else:
            return "NO_TRADE", "score < 0.53 → no trade"

    # SILVER ------------------------------------------------
    if asset == "SILVER":
        if score >= 0.96:
            return "LONG", "score >= 0.96 → Long allowed"
        else:
            return "NO_TRADE", "score < 0.96 → ignore"

    # COPPER ------------------------------------------------
    if asset == "COPPER":
        if score >= 0.56:
            return "LONG", "score >= 0.56 → Long allowed"
        else:
            return "NO_TRADE", "score < 0.56 → no trade"

    # NATURAL GAS ------------------------------------------
    if asset == "NATURAL GAS":
        if score >= 0.56:
            return "LONG", "score >= 0.56 → Long"
        elif score <= 0.44:
            return "SHORT", "score ≤ 0.44 → Short"
        else:
            return "NO_TRADE", "0.44 < score < 0.56 → no trade"

    # FALLBACK ---------------------------------------------
    return "NO_TRADE", "unknown asset"
