#!/usr/bin/env python
# --- coding: utf-8 ---

import json
import os
from os import path
from splinter import Browser
from Config import Config
from bookstore.BookstoreRunner import BookstoreRunner
from alphapolis.AlphapolisRunner import AlphapolisRunner

file = open(path.join(path.abspath(path.dirname(__file__)), 'config.json'), 'r')
data = json.load(file)
file.close()

config = Config(data)

if not path.isdir(config.logDirectory):
    try:
        os.makedirs(config.logDirectory)
    except OSError as exception:
        print("ディレクトリの作成に失敗しました({0})".format(directory))
        raise

log_name = path.join(config.logDirectory, 'ghostdriver.log')

browser = Browser(config.driver, user_agent = config.userAgent, service_log_path = log_name)
browser.driver.set_window_size(config.windowSize['width'], config.windowSize['height'])

while True:
    input_data = input('Input URL > ')
    if input_data == '':
        continue
    elif input_data == 'exit':
        print('Bye.')
        break
    elif BookstoreRunner.check(input_data):
        runner = BookstoreRunner(browser, input_data, config)
    elif AlphapolisRunner.check(input_data):
        runner = AlphapolisRunner(browser, input_data, config)
    else:
        print('入力されたURLはサポートしていません')
        continue

    runner.run()

