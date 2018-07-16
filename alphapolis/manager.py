# --- coding: utf-8 ---
"""
アルファポリスから漫画をダウンロードするためのクラスモジュール
"""

from urllib import request
from os import path
import os
import re


class Manager(object):
    """
    アルファポリスから漫画をダウンロードするクラス
    """

    def __init__(self, directory='./', prefix=''):
        """
        アルファポリスの操作を行うためのコンストラクタ
        @param directory 出力するファイル群を置くディレクトリ
        @param prfix 出力するファイル名のプレフィックス
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
        self._set_directory(directory)
        self._set_prefix(prefix)
        return

    def _set_directory(self, directory):
        """
        ファイルを出力するディレクトリを設定する
        """
        self.directory = directory if (
            directory[-1:] == '/') else directory + '/'
        return

    def _set_prefix(self, prefix):
        """
        出力ファイルのプレフィックス
        """
        self.prefix = prefix
        return

    def start(self, url):
        """
        ページの自動自動ダウンロードを開始する
        @param url アルフォポリスのコンテンツの URL
        """
        self._check_directory(self.directory)
        _sources = self._get_image_urls(url)
        _total = len(_sources)
        for _index in range(_total):
            self._print_progress(_total, _index)
            _response = request.urlopen(_sources[_index])
            if _response.getcode() != 200:
                print('画像の取得に失敗しました(%s)' % _sources[_index])
                continue
            with open('%s%s%03d.png' % (
                    self.directory, self.prefix, _index), 'wb') as file:
                file.write(_response.read())
        self._print_progress(_total, is_end=True)
        return

    def _check_directory(self, directory):
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

    def _print_progress(self, total, current=0, is_end=False):
        """
        進捗を表示する
        @param total ページの総数
        @param current 現在のページ数
        @param 最後のページの場合は True を指定する
        """
        if is_end:
            print('%d/%d' % (total, total))
        else:
            print('%d/%d' % (current, total), end='')
            print('\x1B[10000D', end='', flush=True)
        return

    def _get_image_urls(self, url):
        """
        漫画画像の URL を取得する
        @param url アルファボリスで漫画を表示しているページの URL
        @return ページの URL のリスト
        """
        _response = request.urlopen(url)
        if _response.getcode() != 200:
            print("漫画データの取得に失敗しました")
            return []
        _html = str(_response.read())
        _matches = re.findall(r"var\s+_base\s*=\s*\"([^\"]+)\";", _html)
        if len(_matches) == 0:
            print("漫画情報のURLの取得に失敗しました")
            return []
        _base = _matches[0]
        _matches = re.findall(r"_pages.push\(\"(\d+\.jpg)\"\);", _html)
        if len(_matches) == 0:
            print("漫画のページ情報の取得に失敗しました")
            return []
        return [_base + _page for _page in _matches]
