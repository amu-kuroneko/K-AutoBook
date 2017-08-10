# --- coding: utf-8 ---
"""
アルファポリスの実行クラスモジュール
"""

import re
from AbstractRunner import AbstractRunner
from alphapolis.AlphapolisManager import AlphapolisManager


class AlphapolisRunner(AbstractRunner):
    """
    アルファポリスの実行クラス
    """

    domainPattern = 'www\.alphapolis\.co\.jp'
    """
    サポートするドメイン
    """

    patterns = [
        'manga\/viewManga\/(\?.*no=)?\d+',
        'manga\/official\/\d+/\d+'
    ]
    """
    サポートするアルファポリスのパスの正規表現のパターンのリスト
    """

    def run(self):
        """
        アルファポリスの実行
        """
        destination = input('Output Path > ')
        manager = AlphapolisManager(destination)
        manager.start(self.url)
        return
