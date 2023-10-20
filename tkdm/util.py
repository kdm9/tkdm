
def ask_yesno(prompt, default=True):
    if default:
        prompt += " [Y/n] "
    else:
        prompt += " [y/N] "
    resp = input(prompt)
    if not resp:
        return default
    elif resp.lower()[0] == 'y':
        return True
    else:
        return False
