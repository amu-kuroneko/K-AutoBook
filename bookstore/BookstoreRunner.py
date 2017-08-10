# --- coding: utf-8 ---
"""
ブックストアの実行クラスモジュール
"""

import re
from os import path
from datetime import datetime
from AbstractRunner import AbstractRunner
from bookstore.YahooLogin import YahooLogin
from bookstore.BookstoreManager import BookstoreManager
from bookstore.BoundOnSide import BoundOnSide


class BookstoreRunner(AbstractRunner):
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

    domainPattern = 'bookstore\.yahoo\.co\.jp'
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

    isLogin = False
    """
    ログイン状態
    """

    def run(self):
        """
        ブックストアの実行
        """
        try:
            if (self.config.bookstore.needsLogin and
                    not BookstoreRunner.isLogin and not self.login()):
                return
        except:
            self.browser.driver.save_screenshot(
                path.join(self.config.logDirectory,
                    'login_error_%s.png' % datetime.now().strftime('%s')))
            print('ログイン時にエラーが発生しました')
            return
        print('Loading page of inputed url (%s)' % self.url)
        self.browser.visit(self.url)
        if self.isFull():
            url = self.getFullPageUrl()
            page = self.getFullPageData()
        elif self.isDemo():
            url = self.getDemoPageUrl()
            page = self.getDemoPageData()
        else:
            print('ページの取得に失敗しました')
            return
        if url is None:
            print('コンテンツのURLの取得に失敗しました')
            return
        if page == 0:
            print('ページ数の取得に失敗しました')
            return
        destination = input('Output Path > ')
        manager = BookstoreManager(
            self.browser, self.config.bookstore, destination)
        manager.start(url, page, self.getBoundOnSide())
        return

    def login(self):
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
            BookstoreRunner.isLogin = True
            return True
        return False

    def isFull(self):
        """
        ブックストアの本の内容を全て見れるかどうかを確認する
        @return 全て見れる場合は True を返す
        """
        elements = self.browser.find_by_css('.btn-read > a, p.read > a')
        return len(elements) != 0

    def getFullPageUrl(self):
        """
        全ての内容が見れるページの URL を取得する
        @return 全ての内容が見れるページの URL が存在する場合に URL を返す
        """
        return self.browser.find_by_css('.btn-read > a, p.read > a')[0]['href']

    def isDemo(self):
        """
        ブックストアの本の内容を立ち読みできるかどうかを確認する
        @return 立ち読みできる場合は True を返す
        """
        elements = self.browser.find_by_css('.btn-demo > a')
        return len(elements) != 0

    def getDemoPageUrl(self):
        """
        立ち読みページの URL を取得する
        @return 立ち読みページの URL が存在する場合に URL を返す
        """
        return self.browser.find_by_css('.btn-demo > a')[0]['href']

    def getSpecModuleData(self, title):
        """
        本のスペック情報を取得する
        @param title スペックのタイトル
        @return 該当するスペックが存在する場合はその情報を、ない場合は None を返す
        """
        rows = self.browser.find_by_css('.specModule > table.spec tr')
        for row in rows:
            cells = row.find_by_css('th, td')
            if len(cells) < 2:
                continue
            elif cells[0].text == title:
                return cells[1].text
        return None

    def getFullPageData(self):
        """
        総ページ数を取得する
        @return 取得できた場合にページ数を、取得できなかった場合は 0 を返す
        """
        data = self.getSpecModuleData('総ページ数')
        if data is not None and 3 < len(data):
            return int(data[:-3])
        return 0

    def getDemoPageData(self):
        """
        立ち読みページ数を取得する
        @return 取得できた場合にページ数を、取得できなかった場合に 0 を返す
        """
        data = self.getSpecModuleData('立ち読み\nページ数')
        if data is not None and 3 < len(data):
            return int(data[:-3])
        return 0

    def getBoundOnSide(self):
        for option in self.options:
            if option == self.OPTION_BOUND_ON_LEFT_SIDE:
                return BoundOnSide.LEFT
            elif option == self.OPTION_BOUND_ON_RIGHT_SIDE:
                return BoundOnSide.RIGHT
        return None

    def parseOptions(self, options):
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
        result = []
        if options is not None and options != '':
            checker = re.compile(r'([^\\]|^)(\\{2})*\\$')
            data = ''
            options = options.split(' ')
            last = len(options) - 1
            for index in range(last + 1):
                data = data + options[index]
                if checker.search(data) and index != last:
                    data = data[:-1] + ' '
                elif data != '':
                    result.append(data.replace('\\\\', '\\'))
                    data = ''
        return result
