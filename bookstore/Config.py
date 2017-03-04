# --- coding: utf-8 ---
"""
設定クラスモジュール
"""

from bookstore.ImageFormat import ImageFormat
from bookstore.BoundOnSide import BoundOnSide


class Config(object):
    """
    設定情報を管理するためのクラス
    """

    def __init__(self, data=None):
        """
        設定情報を管理するためのコンストラクタ
        @param data 設定情報
        """
        self.needsLogin = False
        """
        Yahoo! JAPAN にログインする必要があるかどうか
        """
        self.username = None
        """
        Yahoo! JAPAN ID
        """
        self.password = None
        """
        Yahoo! JAPAN ID のパスワード
        """
        self.imageFormat = ImageFormat.JPEG
        """
        書き出す画像フォーマット
        """
        self.sleepTime = 0.5
        """
        ページスクロールのスリープ時間
        """
        self.boundOnSide = BoundOnSide.LEFT
        """
        本の綴じ場所
        """
        if isinstance(data, dict):
            self.update(data)
        return

    def update(self, data):
        """
        設定情報を更新する
        @param data 更新するデータ
        """
        if 'needs_login' in data:
            self.needsLogin = data['needs_login']
        if 'username' in data:
            self.username = data['username']
        if 'password' in data:
            self.password = data['password']
        if 'image_format' in data:
            self.setImageFormat(data['image_format'])
        if 'sleep_time' in data:
            self.sleepTime = data['sleep_time']
        if 'bound_on_side' in data:
            self.setBoundOnSide(data['bound_on_side'])
        return

    def setImageFormat(self, format):
        """
        書き出す画像のフォーマットを設定する
        使用できるフォーマットは bookstore.ImageFormat.ImageFormat に記されている
        @param format 画像のフォーマット
        """
        if isinstance(format, str):
            format = format.upper()
            if format in {ImageFormat.JPEG.name, str(int(ImageFormat.JPEG))}:
                self.imageFormat = ImageFormat.JPEG
            elif format in {ImageFormat.PNG.name, str(int(ImageFormat.PNG))}:
                self.imageFormat = ImageFormat.PNG
        elif isinstance(format, int):
            if format == ImageFormat.JPEG:
                self.imageFormat = ImageFormat.JPEG
            elif format == ImageFormat.PNG:
                self.imageFormat = ImageFormat.PNG
        return

    def setBoundOnSide(self, boundOnSide):
        """
        本の閉じ場所を設定する
        使用できる場所は bookstore.BoundOnSide.BoundOnSide に記されている
        @param boundOnSide 本の綴じ場所
        """
        if isinstance(boundOnSide, str):
            boundOnSide = boundOnSide.upper()
            if boundOnSide in {BoundOnSide.RIGHT.name, str(
                    int(BoundOnSide.RIGHT))}:
                self.boundOnSide = BoundOnSide.RIGHT
            elif boundOnSide in {BoundOnSide.LEFT.name, str(
                    int(BoundOnSide.LEFT))}:
                self.boundOnSide = BoundOnSide.LEFT
        elif isinstance(boundOnSide, int):
            if boundOnSide == BoundOnSide.RIGHT:
                self.boundOnSide = BoundOnSide.RIGHT
            elif boundOnSide == BoundOnSide.LEFT:
                self.boundOnSide = BoundOnSide.LEFT
        return
