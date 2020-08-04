from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from time import sleep 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from oauth2client.service_account import ServiceAccountCredentials

import sys
sys.path.append('tabelog')
from TabelogSearcher import TabelogSearcher

import gspread
import re
import datetime
import traceback
import os
import logging
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = logging.FileHandler("Ameblog.log", mode='a', encoding='utf-8')
handler.setLevel(DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s    %(message)s'))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

chrome_mode="headless"
# chrome_mode=""
driver=None

class AmeblogSearcher():

    def __init__(self):
        self.curl = ""
        self.text = ""
        self.wks = None
        self.rcnt = 1

    def getDriver(self):
        global driver
        if(chrome_mode == "headless"):
            options = webdriver.ChromeOptions()
            #---headlessで動かすために必要なオプション---
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--log-level=1')
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome("./chromedriver.exe") # さっきDLしたchromedriver.exeを使う
            driver.minimize_window()

    def getData(self):
        global driver
        try:
            self.getDriver()

            driver.get("https://ameblo.jp/watabearuki/entrylist.html")
            atag = driver.find_element_by_xpath('//li[@class="skin-borderQuiet" and position() = 1]/div/div[2]/h2/a')
            atag.click()

            cnt = 0

            self.openSpread()
            self.setHeader()

            while(True):
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//a[@class='skinArticleTitle']")))
                self.getPageData()
                driver.find_element_by_xpath("//a[contains(@class,'skin-pagingNext')]").click()
                WebDriverWait(driver, 30).until(EC.visibility_of_element_located((By.XPATH, "//a[contains(@class, 'skin-pagingPrev')]")))
                sleep(1)

                cnt += 1
                if(cnt > 10):
                    break;

        except NoSuchElementException:
            print(driver.current_url)
            print(traceback.format_exc())

        except Exception:
            print(driver.current_url)
            print(traceback.format_exc())


        # print(self.text)
        driver.close()

    def getPageData(self):
        global driver
        ts = TabelogSearcher()
        ts.setMaxRow = 1
        try:
            self.rcnt += 1
            title = driver.find_element_by_xpath("//a[@class='skinArticleTitle']").text
            theme = driver.find_element_by_xpath("//dl[contains(@class,'skin-entryThemes')]/dd").text
            body = driver.find_element_by_xpath("//div[contains(@class,'skin-entryBody')]").text
            url = ""
            area = ""
            shop = ""
            tabelog = ""

            ret = re.search("(http.+$)", body)

            if(ret):
                url = ret.group(1)

            ret = re.search("^(.+)「(.+)」", title)
            if(ret):
                area = ret.group(1)
                shop = ret.group(2)

                tabelog = ts.searchList(area, shop, 0, 0)


            self.wks.update_acell("A" + str(self.rcnt), title)
            self.wks.update_acell("B" + str(self.rcnt), theme)
            self.wks.update_acell("C" + str(self.rcnt), area)
            self.wks.update_acell("D" + str(self.rcnt), shop)
            self.wks.update_acell("E" + str(self.rcnt), url)
            self.wks.update_acell("F" + str(self.rcnt), body)
            self.wks.update_acell("G" + str(self.rcnt), tabelog)

            # self.text += title + "\t" + theme + "\t" + area + "\t" + shop + "\t" + url + "\n"
        except NoSuchElementException:
            print(traceback.format_exc())

    def openSpread(self):
        scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('./WebTrainProject-a52aed0e9fb4.json', scope)
        gc = gspread.authorize(credentials)
        self.wks = gc.open("Watabelog").sheet1
        self.wks.clear()

    def setHeader(self):
        self.wks.update_acell("A" + str(self.rcnt), "タイトル")
        self.wks.update_acell("B" + str(self.rcnt), "テーマ")
        self.wks.update_acell("C" + str(self.rcnt), "エリア")
        self.wks.update_acell("D" + str(self.rcnt), "店名")
        self.wks.update_acell("E" + str(self.rcnt), "URL")
        self.wks.update_acell("F" + str(self.rcnt), "ブログ本文")
        self.wks.update_acell("G" + str(self.rcnt), "食べログ検索結果")



if __name__ == "__main__":
    asobj = AmeblogSearcher()
    asobj.getData()