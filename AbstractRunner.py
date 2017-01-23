# --- coding: utf-8 ---
"""
実行するためのの抽象クラスモジュール
"""

import re
from abc import ABCMeta, abstractmethod

class AbstractRunner(metaclass=ABCMeta):
    """
    実行するための抽象クラス
    """

    domainPattern = ''
    """
    サポートするドメインの正規表現のパターン
    """

    patterns = []
    """
    サポートするパスの正規表現のパターンリスト
    """

    checkers = None
    """
    サポートする URL かどうかの判定機
    """

    @classmethod
    def initializeChecker(cls):
        """
        サポートする URL かどうかの判定機の初期設定を行う
        """
        cls.checkers = []
        for pattern in cls.patterns:
            cls.checkers.append(re.compile('https?:\/\/' + cls.domainPattern + '\/' + pattern))
        return

    @classmethod
    def check(cls, url):
        """
        サポートしているかどうかの判定を行う
        @param url サポートしているどうかを判定する URL
        @return サポートしている場合に True を返す
        """
        if cls.checkers is None:
            cls.initializeChecker()
        for checker in cls.checkers:
            if checker.match(url):
                return True
        return False

    def __init__(self, browser, url, config = None):
        """
        ブックストアで実行するためのコンストラクタ
        @param borwser splinter のブラウザ情報
        """

        self.browser = browser
        """
        splinter のブラウザ情報
        """

        self.url = url
        """
        実行するブックストアの URL
        """

        self.config = config
        """
        設定
        """
        return

    @abstractmethod
    def run(self):
        """
        実行メソッド
        """
        pass
