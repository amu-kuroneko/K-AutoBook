# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

from enum import IntEnum

class ImageFormat(IntEnum):
    """
    書き出す画像のフォーマット
    """

    JPEG = 1
    """
    JPEG フォーマット
    """
    PNG = 2
    """
    PNG フォーマット
    """

