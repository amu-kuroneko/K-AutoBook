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
            cls.checkers.append(
                re.compile(
                    r'https?:\/\/' + cls.domainPattern + '\/' + pattern))
        return

    @classmethod
    def check(cls, url):
        """
        サポートしているかどうかの判定を行う
        @param url str サポートしているどうかを判定する URL
        @return bool サポートしている場合に True を返す
        """
        if cls.checkers is None:
            cls.initializeChecker()
        for checker in cls.checkers:
            if checker.match(url):
                return True
        return False

    def __init__(self, browser, url, config=None, options=None):
        """
        ブックストアで実行するためのコンストラクタ
        @param borwser splinter のブラウザ情報
        @param url str アクセスする URL
        @param config Config 設定情報
        @param options str オプション情報
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

        self.options = self.parseOptions(options)
        """
        オプションとして指定する文字列
        オプションのパース方法は継承先に依存する
        """
        return

    @abstractmethod
    def run(self):
        """
        実行メソッド
        """
        pass

    def parseOptions(self, options):
        """
        オプションのパース処理
        @param options str オプション文字列
        @return str 引数で受け取ったオプション文字列をそのまま返す
        """
        return options
