def reverse_string(text: str) -> str:
    """
    Reverses the given string in a basic manner.
    """
    result = ""
    for char in text:
        result = char + result
    return result
