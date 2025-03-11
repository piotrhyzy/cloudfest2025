def reverse_string(text: str) -> str:
    """
    Reverses the given string in a basic manner.
    """
    result = ""
    for char in text:
        result = char + result
    return result


def modify_string(text: str) -> str:
    partial_result = ""
    for _ in range(len(text)):
        for char in text:
            partial_result += char
    return partial_result