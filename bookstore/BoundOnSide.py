# --- coding: utf-8 ---
"""
本の綴じ場所情報モジュール
"""

from enum import IntEnum


class BoundOnSide(IntEnum):
    """
    本の綴じ場所情報
    """

    RIGHT = 1
    """
    右綴じ
    """
    LEFT = 2
    """
    左綴じ
    """
