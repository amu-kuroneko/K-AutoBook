# --- coding: utf-8 ---
"""
ブックストアの操作を行うためのクラスモジュール
"""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from os import path
from bookstore.config import Config, ImageFormat, BoundOnSide
import os
import time


class Manager(object):
    """
    ブックストアの操作を行うためのクラス
    """

    IMAGE_DIRECTORY = '/tmp/k/'
    """
    画像を一時的に保存するディレクトリ
    """

    CHECK_Y = 100
    """
    画像の色の判定を行う Y 座標
    """

    def __init__(self, browser, config=None, directory='./', prefix=''):
        """
        ブックストアの操作を行うためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.config = config if isinstance(config, Config) else None
        """
        Bookstore の設定情報
        """
        self.directory = None
        """
        ファイルを出力するディレクトリ
        """
        self.prefix = None
        """
        出力するファイルのプレフィックス
        """
        self.next_key = None
        """
        次のページに進むためのキー
        """
        self.previous_key = None
        """
        前のページに戻るためのキー
        """
        self._set_directory(directory)
        self._set_prefix(prefix)
        self._set_bound_of_side(None)
        return

    def _set_directory(self, directory):
        """
        ファイルを出力するディレクトリを設定する
        """
        if directory == '':
            self.directory = './'
            print('Output to current directory')
            return
        _base_path = directory.rstrip('/')
        if _base_path == '':
            _base_path = '/'
        elif not path.exists(_base_path):
            self.directory = _base_path + '/'
            return
        else:
            _base_path = _base_path + '-'
        i = 1
        while path.exists(_base_path + str(i)):
            i = i + 1
        self.directory = _base_path + str(i) + '/'
        print("Change output directory to '%s' because '%s' alreadly exists"
              % (self.directory, directory))
        return

    def _set_prefix(self, prefix):
        """
        出力ファイルのプレフィックス
        """
        self.prefix = prefix
        return

    def start(self, url, number, bound_on_side):
        """
        ページの自動スクリーンショットを開始する
        @param url ブックストアのコンテンツの URL
        @param number そのコンテンツの総ページ数
        @param bound_on_side ページの綴じ場所
        """
        self._set_bound_of_side(bound_on_side)
        self.browser.visit(url)
        time.sleep(2)
        if self._is_warning():
            self._agree_warning()
            time.sleep(2)
        if self._is_showing_description():
            self._close_description()
        self._check_directory(self.IMAGE_DIRECTORY)
        self._check_directory(self.directory)
        _total = self._get_display_page(number)
        _extension = self._get_extension()
        _format = self._get_save_format()
        _sleep_time = (
            self.config.sleep_time if self.config is not None else 0.5)
        self._move_first_page()
        time.sleep(_sleep_time)
        if self._is_last_page():
            self._move_last_page()
            time.sleep(_sleep_time)
        for _index in range(_total):
            self._print_progress(_total, _index)
            if self._is_last_page():
                print("\nLast page.")
                return
            _temporary_page = self.IMAGE_DIRECTORY + 'K-AutoBook' + _extension
            self.browser.driver.save_screenshot(_temporary_page)
            self._next()
            self._triming(_temporary_page, '%s%s%03d%s' % (
                self.directory, self.prefix, _index, _extension), _format)
            time.sleep(_sleep_time)
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

    def _get_display_page(self, page):
        """
        コンテンツの総ページ数から表示されるページ数を取得する
        @param page コンテンツの総ページ数
        @return 表示されるページ数
        """
        return int(page / 2) + 1

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

    def _triming(self, source, destination, format):
        """
        画像の両端の色と異なる色になる場所でトリミングする
        @param source 元となる画像のパス
        @param destination 出力する画像のパス
        @param format 書き出す画像のフォーマット
        """
        _image = Image.open(source)
        _width, _height = _image.size
        _start_x = 0
        _end_x = _width
        _bases = set()
        for _point_y in range(_height):
            _bases.add(_image.getpixel((0, _point_y)))
            _bases.add(_image.getpixel((_width - 1, _point_y)))
        for _point_x in range(_width):
            _pixel = _image.getpixel((_point_x, self.CHECK_Y))
            if not _pixel in _bases:
                _start_x = _point_x
                break
        for _point_x in range(_width)[::-1]:
            _pixel = _image.getpixel((_point_x, self.CHECK_Y))
            if not _pixel in _bases:
                _end_x = _point_x + 1
                break
        _image = _image.crop((_start_x, 0, _end_x, _height))
        if self.config is not None and (
                self.config.image_format == ImageFormat.JPEG):
            _image = _image.convert('RGB')
        _image.save(destination, format.upper())
        return

    def _next(self):
        """
        次のページに進む
        スペースで次のページにすすめるのでスペースキー固定
        """
        self._press_key(Keys.SPACE)
        return

    def _previous(self):
        """
        前のページに戻る
        """
        self._press_key(self.previous_key)
        return

    def _move_first_page(self):
        """
        先頭ページに移動
        """
        self._send_key_on_shift(self.previous_key)

    def _move_last_page(self):
        """
        最後のページに移動
        """
        self._send_key_on_shift(self.next_key)

    def _press_key(self, key):
        """
        指定したキーを押す
        """
        ActionChains(self.browser.driver).key_down(key).perform()
        return

    def _send_key(self, keys):
        """
        指定した文字を送信する
        """
        ActionChains(self.browser.driver).send_keys(keys).perform()
        return

    def _send_key_on_shift(self, keys):
        """
        指定した文字を Shift キーを押した状態で送信する
        """
        _chain = ActionChains(self.browser.driver)
        _chain = _chain.key_down(Keys.SHIFT)
        _chain = _chain.send_keys(keys)
        _chain = _chain.key_up(Keys.SHIFT)
        _chain.perform()

    def _is_warning(self):
        """
        警告文が表示されているかを確認する
        @return 警告文が表示されている場合に True を返す
        """
        _script = 'document.getElementById("binb").contentWindow' + \
            '.document.getElementById("warningPageFrame")'
        try:
            return self.browser.evaluate_script(_script) is not None
        except:
            # 正常に script 出来ない場合は警告文が表示されていないと解釈
            return False

    def _is_last_page(self):
        """
        最後のページかどうかを確認する
        @return 最後のページの場合に True を返す
        """
        return self.browser.url.startswith(
            'https://bookstore.yahoo.co.jp/viewerLastPage')

    def _agree_warning(self):
        """
        警告文に同意してページを表示する
        """
        _script = 'document.getElementById("binb").contentWindow' + \
            '.document.getElementById("warningPageFrame").contentWindow' + \
            '.document.getElementsByClassName("btnOK")[0].click()'
        self.browser.execute_script(_script)

    def _is_showing_description(self):
        """
        説明モーダルが表示されているかを確認する
        @return 説明モーダルが表示されている場合に True を返す
        """
        _script = '''(function(v) {
            if (!(v.b = document.getElementById('binb'))) return '';
            if (!(v.c = v.b.contentWindow)) return '';
            if (!(v.d = v.c.document)) return '';
            if (!(v.m = v.d.getElementById('menu_tips_div'))) return '';
            if (!(v.s = v.m.style)) return '';
            return v.s.visibility;
        })({});'''
        return self.browser.evaluate_script(_script) != 'hidden'

    def _close_description(self):
        """
        説明モーダルを閉じる
        """
        self._send_key('-')
        return

    def _get_extension(self):
        """
        書き出すファイルの拡張子を取得する
        @return 拡張子
        """
        if self.config is not None:
            if self.config.image_format == ImageFormat.JPEG:
                return '.jpg'
            elif self.config.image_format == ImageFormat.PNG:
                return '.png'
        return '.jpg'

    def _get_save_format(self):
        """
        書き出すファイルフォーマットを取得する
        @return ファイルフォーマット
        """
        if self.config is not None:
            if self.config.image_format == ImageFormat.JPEG:
                return 'jpeg'
            elif self.config.image_format == ImageFormat.PNG:
                return 'png'
        return 'jpeg'

    def _set_bound_of_side(self, bound_on_side):
        """
        ページの綴じ場所から次/前のページへの移動キーを設定する
        @param bound_on_side ページの綴じ場所
        """
        _result = BoundOnSide.RIGHT
        if bound_on_side in {BoundOnSide.RIGHT, BoundOnSide.LEFT}:
            _result = bound_on_side
        elif self.config is not None:
            _result = self.config.bound_on_side
        if _result == BoundOnSide.LEFT:
            self.next_key = Keys.ARROW_RIGHT
            self.previous_key = Keys.ARROW_LEFT
        else:
            self.next_key = Keys.ARROW_LEFT
            self.previous_key = Keys.ARROW_RIGHT
        return
