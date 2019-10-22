K-AutoBook
====

# Overview

This program downloads web comics.

## Description

If website is bookstore, K-AutoBook takes a screenshot of page displayed by browser.
Then screenshot is trimmed.
And if website is alphapolis, K-AutoBook downloads image files.

## Requirement

This program is supposed to work on Unix-based OS.

* `Python` Python 3.4.6 or later
* `pip` pip 9.0.1 or later
* `ChromeDriver` ChromeDriver 77.0.3865.40 or later

## Install

    $ cd <install directory>
    $ git clone https://github.com/amu-kuroneko/K-AutoBook.git
    $ cd K-AutoBook
    $ pip install -r requirements.txt

## Usage

    $ cd <install directory>/K-AutoBook
    $ ./k_auto_book.py
    Input URL > <Specify the URL of the page that you want to download>
    Input Captcha > <Characters of image captcha>
    Output Path > <Specify the path that you want to save images>

You can specify the format of URL below.

* `http://ebookjapan.yahoo.co.jp/<number>/<id>`
* `http://www.alphapolis.co.jp/manga/viewManga/<number>`

_**Sample of ebookjapan**_

You can specify the URL of a page that like [this link](https://ebookjapan.yahoo.co.jp/books/145222/A000100547).

_**Sample of Alphaplis**_

You can specify the [URL of the page that is displaied the comics](http://www.alphapolis.co.jp/manga/viewManga/46).  
You must not specify the [URL of list page](http://www.alphapolis.co.jp/manga/viewOpening/138000030/).

## Contribution

Please contact the owner of this repository.

## Author

[kuroneko](https://github.com/amu-kuroneko)

