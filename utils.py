def shorten_string(string, n):
    if len(string) > n:
        return string[:n-3] + "..."
    return string
