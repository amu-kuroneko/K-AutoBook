# --- coding: utf-8 ---
"""
ブックストアの実行クラスモジュール
"""

import re
from os import path
from datetime import datetime
from runner import AbstractRunner
from bookstore.login import YahooLogin
from bookstore.manager import Manager
from bookstore.config import BoundOnSide


class Runner(AbstractRunner):
    """
    ブックストアの実行クラス
    """

    OPTION_BOUND_ON_LEFT_SIDE = 'L'
    """
    左綴じを示すオプション
    """

    OPTION_BOUND_ON_RIGHT_SIDE = 'R'
    """
    右綴じを示すオプション
    """

    domain_pattern = 'bookstore\.yahoo\.co\.jp'
    """
    サポートするドメイン
    """

    patterns = [
        'shoshi-\d+\/$',
        'unlimited\/shoshi-\d+\/$'
    ]
    """
    サポートするブックストアのパスの正規表現のパターンのリスト
    """

    is_login = False
    """
    ログイン状態
    """

    def run(self):
        """
        ブックストアの実行
        """
        try:
            if (self.config.bookstore.needs_login and
                    not Runner.is_login and not self._login()):
                return
        except:
            _filename = 'login_error_%s.png' % datetime.now().strftime('%s')
            self.browser.driver.save_screenshot(
                path.join(self.config.log_directory, _filename))
            print('ログイン時にエラーが発生しました')
            return
        print('Loading page of inputed url (%s)' % self.url)
        self.browser.visit(self.url)
        if self._is_full():
            _url = self._get_full_page_url()
            _page = self._get_full_page_data()
        elif self._is_demo():
            _url = self._get_demo_page_url()
            _page = self._get_demo_page_data()
        else:
            print('ページの取得に失敗しました')
            return
        if _url is None:
            print('コンテンツのURLの取得に失敗しました')
            return
        if _page == 0:
            print('ページ数の取得に失敗しました')
            return
        _destination = input('Output Path > ')
        _manager = Manager(
            self.browser, self.config.bookstore, _destination)
        _manager.start(_url, _page, self._get_bound_of_side())
        return

    def _login(self):
        """
        ログイン処理を行う
        @param borwser splinter のブラウザ情報
        @return ログイン成功時に True を返す
        """
        if self.config.bookstore.username and self.config.bookstore.password:
            yahoo = YahooLogin(
                self.browser,
                self.config.bookstore.username,
                self.config.bookstore.password)
        else:
            yahoo = YahooLogin(self.browser)
        if yahoo.login():
            Runner.is_login = True
            return True
        return False

    def _is_full(self):
        """
        ブックストアの本の内容を全て見れるかどうかを確認する
        @return 全て見れる場合は True を返す
        """
        _elements = self.browser.find_by_css('.btn-read > a, p.read > a')
        return len(_elements) != 0

    def _get_full_page_url(self):
        """
        全ての内容が見れるページの URL を取得する
        @return 全ての内容が見れるページの URL が存在する場合に URL を返す
        """
        return self.browser.find_by_css('.btn-read > a, p.read > a')[0]['href']

    def _is_demo(self):
        """
        ブックストアの本の内容を立ち読みできるかどうかを確認する
        @return 立ち読みできる場合は True を返す
        """
        _elements = self.browser.find_by_css('.btn-demo > a')
        return len(_elements) != 0

    def _get_demo_page_url(self):
        """
        立ち読みページの URL を取得する
        @return 立ち読みページの URL が存在する場合に URL を返す
        """
        return self.browser.find_by_css('.btn-demo > a')[0]['href']

    def _get_spec_module_data(self, title):
        """
        本のスペック情報を取得する
        @param title スペックのタイトル
        @return 該当するスペックが存在する場合はその情報を、ない場合は None を返す
        """
        _rows = self.browser.find_by_css('.specModule > table.spec tr')
        for _row in _rows:
            _cells = _row.find_by_css('th, td')
            if len(_cells) < 2:
                continue
            elif _cells[0].text == title:
                return _cells[1].text
        return None

    def _get_full_page_data(self):
        """
        総ページ数を取得する
        @return 取得できた場合にページ数を、取得できなかった場合は 0 を返す
        """
        _data = self._get_spec_module_data('総ページ数')
        if _data is not None and 3 < len(_data):
            return int(_data[:-3])
        return 0

    def _get_demo_page_data(self):
        """
        立ち読みページ数を取得する
        @return 取得できた場合にページ数を、取得できなかった場合に 0 を返す
        """
        _data = self._get_spec_module_data('立ち読み\nページ数')
        if _data is not None and 3 < len(_data):
            return int(_data[:-3])
        return 0

    def _get_bound_of_side(self):
        for _option in self.options:
            if _option == self.OPTION_BOUND_ON_LEFT_SIDE:
                return BoundOnSide.LEFT
            elif _option == self.OPTION_BOUND_ON_RIGHT_SIDE:
                return BoundOnSide.RIGHT
        return None

    def parse_options(self, options):
        """
        オプションのパース処理
        パース処理は以下のルールに従って行われる
        ・スペースを区切り文字とする
            e.g.) 'aaa bbb' => ['aaa', 'bbb']
        ・スペースはバックスラッシュを前に付けることででエスケープされる
            e.g.) 'aaa\ bbb' => ['aaa bbb']
        ・バックスラッシュはバックスラッシュを前に付けることでエスケープされる
            e.g.) 'aaa\\ bbb' => ['aaa\', 'bbb']
        @param options str オプション文字列
        @return list(str) パースされたオプション情報を持つリスト
        """
        _result = []
        if options is not None and options != '':
            _checker = re.compile(r'([^\\]|^)(\\{2})*\\$')
            _data = ''
            _options = options.split(' ')
            _last = len(_options) - 1
            for _index in range(_last + 1):
                _data = _data + _options[_index]
                if _checker.search(_data) and _index != _last:
                    _data = _data[:-1] + ' '
                elif _data != '':
                    _result.append(_data.replace('\\\\', '\\'))
                    _data = ''
        return _result
