#!/usr/bin/env python
# --- coding: utf-8 ---

import json
import os
import re
from os import path
from PIL import Image
from splinter import Browser
from selenium.webdriver import ChromeOptions
from config import Config
from ebookjapan.runner import Runner as Ebookjapan
from alphapolis.runner import Runner as Alphapolis


def _load_config_data():
    _file = open(
        path.join(path.abspath(path.dirname(__file__)), 'config.json'), 'r')
    _data = json.load(_file)
    _file.close()
    return _data


def _make_directory(directory):
    if not path.isdir(directory):
        try:
            os.makedirs(directory)
        except OSError as exception:
            print("ディレクトリの作成に失敗しました({0})".format(directory))
            raise


def _get_screenshot_size(browser):
    _dirname = '/tmp/k'
    _make_directory(_dirname)
    _filename = _dirname + '/screenshot_size.png'
    if not browser.driver.save_screenshot(_filename):
        return None
    return Image.open(_filename).size


def _set_window_size(browser, window_size):
    _width = window_size['width']
    _height = window_size['height']
    browser.driver.set_window_size(_width, _height)
    _size = _get_screenshot_size(browser)
    if _size is None:
        print('ウィンドウサイズの取得に失敗しました')
        return None
    if _size != (_width, _height):
        _width = int(_width * _width / _size[0])
        _height = int(_height * _height / _size[1])
        browser.driver.set_window_size(_width, _height)
    return True


def _initialize_browser(config):
    log_name = path.join(config.log_directory, 'ghostdriver.log')
    _params = {
        'headless': True,
        'user_agent': config.user_agent,
        'service_log_path': log_name}
    if config.driver == 'chrome':
        _option = ChromeOptions()
        _option.add_argument('--headless')
        _option.add_argument('--no-sandbox')
        _params['chrome_options'] = _option
    _browser = Browser(config.driver, **_params)
    if _set_window_size(_browser, config.window_size) is None:
        return None
    return _browser


def _main():

    _config = Config(_load_config_data())
    _make_directory(_config.log_directory)
    _browser = _initialize_browser(_config)

    if _browser is None:
        return

    _stripper = re.compile(r'^ +')
    while True:
        try:
            _input_data = _stripper.sub('', input('Input URL > '))
        except EOFError:
            print("\nBye.")
            break
        _inputs_data = _input_data.split(' ', 1)
        _url = _inputs_data[0]
        _options = _inputs_data[1] if 1 < len(_inputs_data) else None
        if _input_data == '':
            continue
        elif _input_data == 'exit':
            print('Bye.')
            break
        elif Ebookjapan.check(_url):
            _runner = Ebookjapan(_browser, _input_data, _config, _options)
        elif Alphapolis.check(_url):
            _runner = Alphapolis(_browser, _input_data, _config, _options)
        else:
            print('入力されたURLはサポートしていません')
            continue

        _runner.run()


_main()
