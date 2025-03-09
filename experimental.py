from typing import Optional

def check_value(x: Optional[int]) -> bool:
    # Possibly returns True if x is not None and passes a certain condition
    return x is not None and x > 10
