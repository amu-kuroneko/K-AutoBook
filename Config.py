# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

import bookstore.Config

class Config(object):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self, data = None):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
        """
        self.driver = 'phantomjs'
        """
        開くブラウザのドライバ
        """
        self.userAgent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.95 Safari/537.36'
        """
        User Agent
        """
        self.windowSize = {'width': 2880, 'height': 1800 }
        """
        ウィンドウサイズ
        width: 横幅
        height: 高さ
        """
        self.logDirectory = '/tmp/k_auto_book/'
        """
        ログを出力するディレクトリパス
        """
        self.bookstore = bookstore.Config.Config()
        """
        Bookstore の設定情報
        """
        if isinstance(data, dict):
            self.update(data)
        return

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        if 'driver' in data:
            self.driver = data['driver']
        if 'user_agent' in data:
            self.userAgent = data['user_agent']
        if 'window_size' in data:
            if 'width' in data['window_size']:
                self.windowSize['width'] = int(data['window_size']['width'])
            if 'heigth' in data['window_size']:
                self.windowSize['height'] = int(data['window_size']['height'])
        if 'log_directory' in data:
            self.logDirectory = data['log_directory']
        if 'bookstore' in data:
            self.bookstore.update(data['bookstore'])
        return

