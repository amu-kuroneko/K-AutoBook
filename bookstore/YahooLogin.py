# --- coding: utf-8 ---
"""
ブックストアを使用するためにYahooアカウントでログインするためのクラスモジュール
"""
from selenium.common.exceptions import InvalidElementStateException
from getpass import getpass
from urllib import request
from PIL import Image
from os import path
import os
import io
import time


class YahooLogin(object):
    """
    Yahooアカウントでログインするためのクラス
    """

    LOGIN_URL = 'https://login.yahoo.co.jp/config/login'
    """
    ログインページの URL
    """

    YAHOO_JAPAN_URL = 'https://www.yahoo.co.jp/'
    """
    Yahoo! JAPAN の URL
    """

    ONE_TIME_PASSWORD_URL = 'https://protect.login.yahoo.co.jp/otp/auth'
    """
    ログイン時にワンタイムパスワードを求めるページの URL
    """

    def __init__(self, browser, yahooId=None, password=None):
        """
        Yahoo でログインするためのコンストラクタ
        @param browser splinter のブラウザインスタンス
        @param yahooId ヤフー ID
        @param password パスワード
        """
        self.browser = browser
        """
        splinter のブラウザインスタンス
        """
        self.yahooId = yahooId
        """
        Yahoo ID
        None が設定されている場合はユーザ入力を求める
        """
        self.password = password
        """
        パスワード
        None が設定されている場合はユーザ入力を求める
        """
        return

    def login(self):
        """
        ログインを行う
        @return ログイン成功時に True を返す
        """
        print('Loading Yahoo JAPAN! top page')
        self.browser.visit(self.YAHOO_JAPAN_URL)
        print('Loading login page')
        self.browser.click_link_by_text('ログイン')
        for count in range(4):
            yahooId = input('Input Yahoo ID > ') if (
                self.yahooId is None) else self.yahooId
            password = getpass('Input Password > ') if (
                self.password is None) else self.password
            print('Trying login: ' + yahooId)
            self.browser.fill('login', yahooId)
            print('Confirm Yahoo JAPAN! ID')
            self.browser.find_by_id('btnNext').click()
            time.sleep(1)
            self.browser.execute_script(
                'element = document.getElementById("passwd");' + \
                'element.disabled = false;' + \
                'element.readOnly = false;')
            self.browser.fill('passwd', password)
            self.browser.find_by_id('btnSubmit').click()
            print('Trying login')
            if self.isLoginError():
                print('ログインに失敗しました')
                if self.yahooId is not None and self.password is not None:
                    return False
                continue
            for count in range(3):
                if self.isImageCaptcha():
                    if not self.showImageCaptcha():
                        return False
                    result = input('Input Captcha > ')
                    self.browser.fill('captchaAnswer', result)
                    self.browser.find_by_css('input[type=image]').first.click()
                elif self.isLoginPage():
                    break
                else:
                    break
                if count == 2 and self.isImageCaptcha():
                    print('画像キャプチャが一致しませんでした')
                    return False
            if not self.isLoginPage():
                oneTimePassword = None
                isSucceededLogin = False
                for count in range(4):
                    if self.isRequiredOneTimePassword():
                        if oneTimePassword is not None:
                            print('Invalid one time password')
                        oneTimePassword = input('Input one time password > ')
                        self.browser.fill('verify_code', oneTimePassword)
                        self.browser.find_by_css('[type=submit]')[0].click()
                    else:
                        isSucceededLogin = True
                        break
                print('Succeeded login')
                return True
        return False

    def isLoginPage(self):
        """
        ログインページかどうかを判定する
        """
        return self.browser.url.startswith(self.LOGIN_URL)

    def isLoginError(self):
        """
        ログインエラーかどうかを判定する
        @return ログインエラーの場合に True を返す
        """
        elements = self.browser.find_by_css('div.yregertxt > h2.yjM')
        return self.isLoginPage() and len(elements) != 0

    def isImageCaptcha(self):
        """
        画像キャプチャに引っかかっているかどうかを取得する
        @return 画像キャプチャをもとめられている場合に True を返す
        """
        result = self.browser.url.startswith(self.LOGIN_URL)
        result = result and self.browser.title == '文字認証を行います。 - Yahoo! JAPAN'
        if result:
            names = []
            for input in self.browser.find_by_tag('input'):
                names.append(input['name'])
            checks = [
                'captchaCdata',
                'captchaMultiByteCaptchaId',
                'captchaView',
                'captchaClassInfo',
                'captchaAnswer'
            ]
            for check in checks:
                result = result and check in names
                if not result:
                    return result
        return result

    def showImageCaptcha(self):
        """
        画像キャプチャを表示する
        @return 画像の表示に成功した場合に True を返す
        """
        file = io.BytesIO(request.urlopen(self.browser.find_by_id(
            'captchaV5MultiByteCaptchaImg')['src']).read())
        baseImage = Image.open(file)
        baseImage = baseImage.convert('RGBA')
        showImage = Image.new('RGBA', baseImage.size, (0xFF, 0xFF, 0xFF, 0x0))
        width, height = baseImage.size
        for pointX in range(width):
            for pointY in range(height):
                pixel = baseImage.getpixel((pointX, pointY))
                if pixel != (0, 0, 0, 0):
                    showImage.putpixel((pointX, pointY), pixel)
        showImage.show()
        return True

    def isRequiredOneTimePassword(self):
        """
        ワンタイムパスワードを求められているかを確認する
        """
        return self.browser.url.startswith(self.ONE_TIME_PASSWORD_URL)
