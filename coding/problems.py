"""
A small local bank of coding problems used by the Coding Interview
mode, each with a reference function name and test cases so
submissions can be auto-graded.
"""

CODING_PROBLEMS = [
    {
        "title": "Two Sum",
        "difficulty": "Easy",
        "statement": "Given a list of integers `nums` and a target integer `target`, "
        "return the indices of the two numbers that add up to target.",
        "constraints": "Exactly one valid answer exists. You may not use the same element twice.",
        "function_name": "two_sum",
        "signature": "def two_sum(nums, target):",
        "starter_code": "def two_sum(nums, target):\n    # your code here\n    pass\n",
        "examples": [{"input": "[2, 7, 11, 15], target=9", "output": "[0, 1]"}],
        "test_cases": [
            {"input": [[2, 7, 11, 15], 9], "expected": [0, 1]},
            {"input": [[3, 2, 4], 6], "expected": [1, 2]},
            {"input": [[3, 3], 6], "expected": [0, 1]},
        ],
    },
    {
        "title": "Reverse a String",
        "difficulty": "Easy",
        "statement": "Given a string `s`, return the string reversed.",
        "constraints": "Do not use slicing tricks like s[::-1] if you want to demonstrate manual logic (either is accepted).",
        "function_name": "reverse_string",
        "signature": "def reverse_string(s):",
        "starter_code": "def reverse_string(s):\n    # your code here\n    pass\n",
        "examples": [{"input": "'hello'", "output": "'olleh'"}],
        "test_cases": [
            {"input": ["hello"], "expected": "olleh"},
            {"input": [""], "expected": ""},
            {"input": ["a"], "expected": "a"},
        ],
    },
    {
        "title": "FizzBuzz",
        "difficulty": "Easy",
        "statement": "Given an integer `n`, return a list of strings from 1 to n where: "
        "multiples of 3 are 'Fizz', multiples of 5 are 'Buzz', multiples of both are 'FizzBuzz', "
        "otherwise the number as a string.",
        "constraints": "1 <= n <= 10000",
        "function_name": "fizzbuzz",
        "signature": "def fizzbuzz(n):",
        "starter_code": "def fizzbuzz(n):\n    # your code here\n    pass\n",
        "examples": [{"input": "5", "output": "['1','2','Fizz','4','Buzz']"}],
        "test_cases": [
            {"input": [5], "expected": ["1", "2", "Fizz", "4", "Buzz"]},
            {"input": [15], "expected": [
                "1", "2", "Fizz", "4", "Buzz", "Fizz", "7", "8", "Fizz", "Buzz",
                "11", "Fizz", "13", "14", "FizzBuzz"
            ]},
        ],
    },
    {
        "title": "Is Palindrome",
        "difficulty": "Easy",
        "statement": "Given a string `s`, return True if it is a palindrome (reads the same "
        "forwards and backwards), ignoring case, otherwise False.",
        "constraints": "Assume only alphanumeric characters, no punctuation.",
        "function_name": "is_palindrome",
        "signature": "def is_palindrome(s):",
        "starter_code": "def is_palindrome(s):\n    # your code here\n    pass\n",
        "examples": [{"input": "'racecar'", "output": "True"}],
        "test_cases": [
            {"input": ["racecar"], "expected": True},
            {"input": ["hello"], "expected": False},
            {"input": ["Level"], "expected": True},
        ],
    },
    {
        "title": "Find Maximum Subarray Sum",
        "difficulty": "Medium",
        "statement": "Given a list of integers `nums`, return the largest sum of any "
        "contiguous subarray (Kadane's algorithm).",
        "constraints": "The list has at least one element.",
        "function_name": "max_subarray",
        "signature": "def max_subarray(nums):",
        "starter_code": "def max_subarray(nums):\n    # your code here\n    pass\n",
        "examples": [{"input": "[-2,1,-3,4,-1,2,1,-5,4]", "output": "6"}],
        "test_cases": [
            {"input": [[-2, 1, -3, 4, -1, 2, 1, -5, 4]], "expected": 6},
            {"input": [[1]], "expected": 1},
            {"input": [[5, 4, -1, 7, 8]], "expected": 23},
        ],
    },
    {
        "title": "Valid Parentheses",
        "difficulty": "Medium",
        "statement": "Given a string `s` containing just the characters '(', ')', '{', '}', "
        "'[' and ']', determine if the input string is valid (properly matched and nested).",
        "constraints": "String length can be 0.",
        "function_name": "is_valid_parens",
        "signature": "def is_valid_parens(s):",
        "starter_code": "def is_valid_parens(s):\n    # your code here\n    pass\n",
        "examples": [{"input": "'()[]{}'", "output": "True"}],
        "test_cases": [
            {"input": ["()[]{}"], "expected": True},
            {"input": ["(]"], "expected": False},
            {"input": ["([)]"], "expected": False},
            {"input": ["{[]}"], "expected": True},
        ],
    },
]


def get_problem_by_difficulty(difficulty: str):
    import random

    matches = [p for p in CODING_PROBLEMS if p["difficulty"] == difficulty]
    pool = matches or CODING_PROBLEMS
    return random.choice(pool)
