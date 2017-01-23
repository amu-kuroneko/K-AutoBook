# --- coding: utf-8 ---
"""
アルファポリスから漫画をダウンロードするためのクラスモジュール
"""

from urllib import request
from lxml import html
from os import path
import os

class AlphapolisManager(object):
    """
    アルファポリスから漫画をダウンロードするクラス
    """

    def __init__(self, directory = './', prefix = ''):
        """
        アルファポリスの操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
        self.setDirectory(directory)
        self.setPrefix(prefix)
        return

    def setDirectory(self, directory):
        """
        ファイルを出力するディレクトリを設定する
        """
        self.directory = directory if directory[-1:] == '/' else directory + '/'
        return

    def setPrefix(self, prefix):
        """
        出力ファイルのプレフィックス
        """
        self.prefix = prefix
        return

    def start(self, url):
        """
        ページの自動自動ダウンrノードを開始する
        @param url アルフォポリスのコンテンツの URL
        """
        self.checkDirectory(self.directory)
        sources = self.getImageUrls(url)
        total = len(sources)
        for index in range(total):
            self.printProgress(total, index)
            response = request.urlopen(sources[index])
            if response.getcode() != 200:
                print('画像の取得に失敗しました(%s)' % sources[index])
                continue
            with open('%s%s%03d.png' % (self.directory, self.prefix, index), 'wb') as file:
                file.write(response.read())
        self.printProgress(total, isEnd = True)
        return

    def checkDirectory(self, directory):
        """
        ディレクトリの存在を確認して，ない場合はそのディレクトリを作成する
        @param directory 確認するディレクトリのパス
        """
        if not path.isdir(directory):
            try:
                os.makedirs(directory)
            except OSError as exception:
                print("ディレクトリの作成に失敗しました({0})".format(directory))
                raise
        return

    def printProgress(self, total, current = 0, isEnd = False):
        """
        進捗を表示する
        @param total ページの総数
        @param current 現在のページ数
        @param 最後のページの場合は True を指定する
        """
        if isEnd:
            print('%d/%d' % (total, total))
        else:
            print('%d/%d' % (current, total), end='')
            print('\x1B[10000D', end='', flush=True)
        return

    def getImageUrls(self, url):
        """
        漫画画像の URL を取得する
        @param url アルファボリスで漫画を表示しているページの URL
        @return ページの URL のリスト
        """
        response = request.urlopen(url)
        if response.getcode() != 200:
            print("漫画データの取得に失敗しました")
            return []
        root = html.fromstring(response.read())
        images = root.cssselect('.manga_image')
        data = {}
        for image in images:
            page = int(image.getparent().attrib['page'])
            data[page] = image.attrib['src']
        result = []
        for key, value in sorted(data.items()):
            result.append(value)
        return result


