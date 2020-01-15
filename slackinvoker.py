# coding: utf-8

from slackbot.bot import Bot
from slackbot.bot import respond_to
from slackbot.bot import listen_to

import re
import datetime
import os
from XyzSearcher import XyzSearcher

flg = 0
ym = ""
xs = None
def main():
    global xs
    xs  = XyzSearcher()
    bot = Bot()
    bot.run()

@listen_to(r'^\?')
def prompt(message):
    xs = XyzSearcher()
    message.reply("\n通常検索：s [場所]、[カテゴリ]\n短縮検索：x [場所]、[検索ワード]\nハイランク検索：sh [場所]、[検索ワード]")

@listen_to(r'^[cC]')
def catalogList(message):
    message.reply(xs.catlist())

@listen_to(r'^[sxSX][h]? ')
def search(message):
    ret = re.match(r"^[sxSX][h]? (.*)、(.+)",message.body['text'])
    area = "";cat = ""
    mode = 0
    hg = 0

    if(ret):
        area = ret.group(1)
        cat = ret.group(2)
    else:
        message.reply("\ns [場所]、[カテゴリ]の形式で入力してください。")

    # mode = 1 if re.search(r"^[xX]", message.body['text']) else 0
    # hg = 1 if re.search(r"^[a-zA-Z][h]", message.body['text']) else 0

    message.send("検索します。お待ちください。")
    print("{0:%Y/%m/%d %H:%M:%S}".format(datetime.datetime.now()) + " ☆FavoriteSearch Start")
    message.reply(xs.searchList(area, cat))
    print("{0:%Y/%m/%d %H:%M:%S}".format(datetime.datetime.now()) + " ☆FavoriteSearch End")

    message.send(xs.getCurrentUrl())


if __name__ == "__main__":
    print('starting favorite search☆')
    main()
