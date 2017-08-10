# --- coding: utf-8 ---
"""
ブックストアの操作を行うためのクラスモジュール
"""

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from PIL import Image
from os import path
from bookstore.ImageFormat import ImageFormat
from bookstore.BoundOnSide import BoundOnSide
from bookstore.Config import Config
import os
import time


class BookstoreManager(object):
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
        self.nextKey = None
        """
        次のページに進むためのキー
        """
        self.previousKey = None
        """
        前のページに戻るためのキー
        """
        self.setDirectory(directory)
        self.setPrefix(prefix)
        self.setBoundOfSide(None)
        return

    def setDirectory(self, directory):
        """
        ファイルを出力するディレクトリを設定する
        """
        self.directory = directory if (
            directory[-1:] == '/') else directory + '/'
        return

    def setPrefix(self, prefix):
        """
        出力ファイルのプレフィックス
        """
        self.prefix = prefix
        return

    def start(self, url, number, boundOnSide):
        """
        ページの自動スクリーンショットを開始する
        @param url ブックストアのコンテンツの URL
        @param number そのコンテンツの総ページ数
        @param boundOnSide ページの綴じ場所
        """
        self.setBoundOfSide(boundOnSide)
        self.browser.visit(url)
        time.sleep(2)
        if self.isWarning():
            self.agreeWarning()
            time.sleep(2)
        if self.isShowingDescription():
            self.closeDescription()
        self.checkDirectory(self.IMAGE_DIRECTORY)
        self.checkDirectory(self.directory)
        total = self.getDisplayPage(number)
        extension = self.getExtension()
        format = self.getSaveFormat()
        sleepTime = self.config.sleepTime if self.config is not None else 0.5
        self.moveFirstPage()
        time.sleep(sleepTime)
        if self.isLastPage():
            self.moveLastPage()
            time.sleep(sleepTime)
        for index in range(total):
            self.printProgress(total, index)
            if self.isLastPage():
                print("\nLast page.")
                return
            temporaryPath = self.IMAGE_DIRECTORY + 'K-AutoBook' + extension
            self.browser.driver.save_screenshot(temporaryPath)
            self.next()
            self.triming(temporaryPath, '%s%s%03d%s' % (
                self.directory, self.prefix, index, extension), format)
            time.sleep(sleepTime)
        self.printProgress(total, isEnd=True)
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

    def getDisplayPage(self, page):
        """
        コンテンツの総ページ数から表示されるページ数を取得する
        @param page コンテンツの総ページ数
        @return 表示されるページ数
        """
        return int(page / 2) + 1

    def printProgress(self, total, current=0, isEnd=False):
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

    def triming(self, source, destination, format):
        """
        画像の両端の色と異なる色になる場所でトリミングする
        @param source 元となる画像のパス
        @param destination 出力する画像のパス
        @param format 書き出す画像のフォーマット
        """
        image = Image.open(source)
        width, height = image.size
        startX = 0
        endX = width
        base = image.getpixel((startX, self.CHECK_Y))
        for pointX in range(width):
            pixel = image.getpixel((pointX, self.CHECK_Y))
            if base != pixel:
                startX = pointX
                break
        for pointX in range(width)[::-1]:
            pixel = image.getpixel((pointX, self.CHECK_Y))
            if base != pixel:
                endX = pointX + 1
                break
        image.crop((startX, 0, endX, height)).save(destination, 'jpeg')
        return

    def next(self):
        """
        次のページに進む
        スペースで次のページにすすめるのでスペースキー固定
        """
        self.pressKey(Keys.SPACE)
        return

    def previous(self):
        """
        前のページに戻る
        """
        self.pressKey(self.previousKey)
        return

    def moveFirstPage(self):
        """
        先頭ページに移動
        """
        self.sendKeyOnShift(self.previousKey)

    def moveLastPage(self):
        """
        最後のページに移動
        """
        self.sendKeyOnShift(self.nextKey)

    def pressKey(self, key):
        """
        指定したキーを押す
        """
        ActionChains(self.browser.driver).key_down(key).perform()
        return

    def sendKey(self, keys):
        """
        指定した文字を送信する
        """
        ActionChains(self.browser.driver).send_keys(keys).perform()
        return

    def sendKeyOnShift(self, keys):
        """
        指定した文字を Shift キーを押した状態で送信する
        """
        ActionChains(self.browser.driver).key_down(Keys.SHIFT).send_keys(keys).key_up(Keys.SHIFT).perform()

    def isWarning(self):
        """
        警告文が表示されているかを確認する
        @return 警告文が表示されている場合に True を返す
        """
        script = 'document.getElementById("binb").contentWindow' + \
            '.document.getElementById("warningPageFrame")'
        return self.browser.evaluate_script(script) is not None

    def isLastPage(self):
        """
        最後のページかどうかを確認する
        @return 最後のページの場合に True を返す
        """
        if self.browser.find_by_id('binb') != []:
            with self.browser.get_iframe('binb') as binb_iframe:
                for iframe in binb_iframe.find_by_tag('iframe'):
                    if iframe['id'] == 'lastPageFrame':
                        return True
        return False

    def agreeWarning(self):
        """
        警告文に同意してページを表示する
        """
        script = 'document.getElementById("binb").contentWindow' + \
            '.document.getElementById("warningPageFrame").contentWindow' + \
            '.document.getElementsByClassName("btnOK")[0].click()'
        self.browser.execute_script(script)

    def isShowingDescription(self):
        """
        説明モーダルが表示されているかを確認する
        @return 説明モーダルが表示されている場合に True を返す
        """
        script = 'document.getElementById("binb").contentWindow' + \
            '.document.getElementById("menu_tips_div").style.visibility'
        return self.browser.evaluate_script(script) != 'hidden'

    def closeDescription(self):
        """
        説明モーダルを閉じる
        """
        self.sendKeys('-')
        return

    def getExtension(self):
        """
        書き出すファイルの拡張子を取得する
        @return 拡張子
        """
        if self.config is not None:
            if self.config.imageFormat == ImageFormat.JPEG:
                return '.jpg'
            elif self.config.imageFormat == ImageFormat.PNG:
                return '.png'
        return '.jpg'

    def getSaveFormat(self):
        """
        書き出すファイルフォーマットを取得する
        @return ファイルフォーマット
        """
        if self.config is not None:
            if self.config.imageFormat == ImageFormat.JPEG:
                return 'jpeg'
            elif self.config.imageFormat == ImageFormat.PNG:
                return 'png'
        return 'jpeg'

    def setBoundOfSide(self, boundOnSide):
        """
        ページの綴じ場所から次/前のページへの移動キーを設定する
        @param boundOnSide ページの綴じ場所
        """
        result = BoundOnSide.RIGHT
        if boundOnSide in {BoundOnSide.RIGHT, BoundOnSide.LEFT}:
            result = boundOnSide
        elif self.config is not None:
            result = self.config.boundOnSide
        if result == BoundOnSide.LEFT:
            self.nextKey = Keys.ARROW_RIGHT
            self.previousKey = Keys.ARROW_LEFT
        else:
            self.nextKey = Keys.ARROW_LEFT
            self.previousKey = Keys.ARROW_RIGHT
        return
