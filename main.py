import argparse
from math_utils import calculate_factorial, sort_data  # Import sort_data as well, in case we need it later.


def main():
    parser = argparse.ArgumentParser(description="Calculate the factorial of a number or sort a list.")
    parser.add_argument("-f", "--factorial", type=int, help="Calculate the factorial of this number")
    parser.add_argument("-s", "--sort", nargs="+", type=int, help="Sort this list of numbers")

    args = parser.parse_args()

    if args.factorial is not None:
        value = args.factorial
        result = calculate_factorial(value)
        print(f"Factorial of {value} is {result}")
    elif args.sort is not None:
        nums = args.sort
        sorted_nums = sort_data(nums)
        print(f"Sorted list: {sorted_nums}")
    else:
        print("Please provide either a number for factorial calculation (-f) or a list of numbers for sorting (-s).")


if __name__ == "__main__":
    main()
