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
