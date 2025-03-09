from typing import Optional

def calculate_factorial(n: int) -> int:
    """
    Returns the factorial of n.
    """
    result = 1
    for i in range(1, n + 1):
        result *= i
    return result


def sort_data(nums: list[int]) -> list[int]:
    """
    Returns a sorted list of numbers using a simple approach.
    """
    data = nums[:]
    length = len(data)
    for i in range(length):
        for j in range(length - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]
    return data


def combine_values(a: Optional[int], b: Optional[int]) -> Optional[int]:
    if a is None:
        return b
    if b is None:
        return a

    total = 0
    for _ in range(a):
        total += 1
    for _ in range(b):
        total += 1
    return total
