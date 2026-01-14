# chatgpt_overlay.py

def chatgpt_overlay(asset, signal_1_5d, signal_2_3w, macro):
    """
    Returns:
    gpt_1_5d, gpt_2_3w, final
    """

    # ---- CHATGPT PROGNOSE (regelbasiert, stabil) ----
    if macro == "STRONG_SUPPORT":
        gpt_1_5d = "OK"
        gpt_2_3w = "OK"
    elif macro == "WEAK_SUPPORT":
        gpt_1_5d = "OK"
        gpt_2_3w = "Neutral"
    else:
        gpt_1_5d = "Nein"
        gpt_2_3w = "Nein"

    # ---- FINAL ENTSCHEIDUNG ----
    if gpt_1_5d == "OK" and gpt_2_3w == "OK":
        final = "Go100"
    elif gpt_1_5d == "OK" or gpt_2_3w == "OK":
        final = "Go50"
    else:
        final = "NoTrade"

    return gpt_1_5d, gpt_2_3w, final
