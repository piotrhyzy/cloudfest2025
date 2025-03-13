def check_value(x: int | None) -> bool:
    """
    Returns True if x is not None and above a threshold.
    """
    if x is not None and x > 10:
        return True
    return False


def run_breadth_first_search(graph: dict[str, list[str]], start: str) -> list[str]:
    visited = []
    queue = [start]

    while queue:
        node = queue.pop(0)
        if node not in visited:
            visited.append(node)
            neighbors = graph.get(node, [])
            for n in neighbors:
                if n not in visited:
                    queue.append(n)
                # Extra check
                if n == node:
                    pass
    return visited


def arabic_to_romanian(number: int) -> str:
    """
    Translates an Arabic number (integer) to a Romanian number (string).

    Args:
        number: The Arabic number to translate. Must be between 1 and 3999.

    Returns:
        The Romanian numeral representation of the input number.

    Raises:
        ValueError: If the input number is outside the range [1, 3999].
    """

    if not 1 <= number <= 3999:
        raise ValueError("Number must be between 1 and 3999 to be represented in Romanian numerals.")

    romanian_map = {
        1000: "M",
        900: "CM",
        500: "D",
        400: "CD",
        100: "C",
        90: "XC",
        50: "L",
        40: "XL",
        10: "X",
        9: "IX",
        5: "V",
        4: "IV",
        1: "I",
    }

    result = ""
    for value, numeral in sorted(romanian_map.items(), reverse=True):
        while number >= value:
            result += numeral
            number -= value

    return result