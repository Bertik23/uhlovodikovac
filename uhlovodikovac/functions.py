import math
from typing import Any

def addYL(s: str) -> str:
    return s + "yl"

def removeBlank(l: list) -> list:
    lOut = []
    for i in l:
        if i != "":
            lOut.append(i)
    return lOut

def oddEven(num: float) -> int:
    if num%2 == 0:
        return 1
    else:
        return -1

def positiveOrNagative(num: float) -> int:
    if num > 0:
        return 1
    elif num < 0:
        return -1
    else:
        return 0

def rstripIfEndingWith(s: str, chars: str) -> str:
    if s.endswith(chars):
        return s.rstrip(chars)
    else:
        return s

def lstripIfEndingWith(s: str, chars: str) -> str:
    if s.startswith(chars):
        return s.lstrip(chars)
    else:
        return s

def ifString(s: Any) -> str:
    if type(s) == str:
        return s
    else:
        return ""

def maxOrZero(l: list) -> float:
    try:
        return max(l)
    except ValueError:
        return -math.inf

def minOrZero(l: list) -> float:
    try:
        return min(l)
    except ValueError:
        return math.inf