# chatgpt_overlay.py

def chatgpt_overlay(asset, signal_1_5d, signal_2_3w, macro):
    """
    returns:
    chatgpt_1_5d, chatgpt_2_3w, final
    """

    # ---- RULE BASE (stabil, kein ML) ----
    if macro == "STRONG_SUPPORT":
        gpt_1_5d = "OK"
        gpt_2_3w = "OK"
    elif macro == "WEAK_SUPPORT":
        gpt_1_5d = "OK"
        gpt_2_3w = "Neutral"
    else:
        gpt_1_5d = "Nein"
        gpt_2_3w = "Nein"

    # ---- FINAL LOGIC ----
    if gpt_1_5d == "OK" and gpt_2_3w == "OK":
        final = "Go100"
    elif "OK" in [gpt_1_5d, gpt_2_3w]:
        final = "Go50"
    else:
        final = "NoTrade"

    return gpt_1_5d, gpt_2_3w, final
