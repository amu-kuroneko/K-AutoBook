#!/usr/bin/env python
# --- coding: utf-8 ---

import json
import os
import re
from os import path
from splinter import Browser
from Config import Config
from bookstore.BookstoreRunner import BookstoreRunner
from alphapolis.AlphapolisRunner import AlphapolisRunner

file = open(
    path.join(path.abspath(path.dirname(__file__)), 'config.json'), 'r')
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

browser = Browser(
    config.driver, user_agent=config.userAgent, service_log_path=log_name)
browser.driver.set_window_size(
    config.windowSize['width'], config.windowSize['height'])

stripper = re.compile(r'^ +')
while True:
    try:
        input_data = stripper.sub('', input('Input URL > '))
    except EOFError:
        print("\nBye.")
        break
    inputs_data = input_data.split(' ', 1)
    url = inputs_data[0]
    options = inputs_data[1] if 1 < len(inputs_data) else None
    if input_data == '':
        continue
    elif input_data == 'exit':
        print('Bye.')
        break
    elif BookstoreRunner.check(url):
        runner = BookstoreRunner(browser, input_data, config, options)
    elif AlphapolisRunner.check(url):
        runner = AlphapolisRunner(browser, input_data, config, options)
    else:
        print('入力されたURLはサポートしていません')
        continue

    runner.run()
