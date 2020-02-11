from selenium import webdriver # さっきpip install seleniumで入れたseleniumのwebdriverというやつを使う
from selenium.common.exceptions import NoSuchElementException
from oauth2client.service_account import ServiceAccountCredentials
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from time import sleep 
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import re
import datetime
import yaml
import sys
import traceback
import os
import urllib.parse

import logging
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = logging.FileHandler("Favorite.log", mode='a', encoding='utf-8')
handler.setLevel(DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s    %(message)s'))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

chrome_mode="headless"
# chrome_mode=""
driver=None
max_row = 10

class XyzSearcher():

    def __init__(self):
        self.curl = ""
        self.catlist = []

    def getDriver(ts):
        global driver
        if(chrome_mode == "headless"):
            options = webdriver.ChromeOptions()
            #---headlessで動かすために必要なオプション---
            options.add_argument("--headless")
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--log-level=1')
            driver = webdriver.Chrome(options=options)
        else:
            driver = webdriver.Chrome("./chromedriver.exe") # さっきDLしたchromedriver.exeを使う
            driver.minimize_window()


    def getCategory(ts):
        global driver

        jflg = False
        ts.getDriver()

        driver.get("http://xn--qck4e3a468yfxr0q3azkrifd985b.xyz/")

        clist = driver.find_elements_by_xpath("//li[contains(@class,'cat-item')]")

        for w in clist:
            aobj = w.find_element_by_xpath("./a")
            cat = re.sub("^.+cat=","",aobj.get_attribute("href"))
            label = aobj.get_attribute("innerText")
            if(label == "ジャンル"):
                jflg = True
            
            if(jflg):
                ts.catlist.append("[" + cat + "] " + label)

        driver.close()

    def createCategoryString(ts):
        ret = ""
        for w in ts.catlist:
            ret += w + "\n"
        return ret
    
    def searchList(ts, area, cat):
        global driver
        retstr = ""

        try:
            ts.getDriver()

            driver.get("http://xn--qck4e3a468yfxr0q3azkrifd985b.xyz/?s=" + area + "&cat=" + cat)
            # driver.get("http://xn--qck4e3a468yfxr0q3azkrifd985b.xyz/?s=%E9%8A%80%E5%BA%A7&cat=191&paged=8")
            
            ts.curl = driver.current_url

            retstr += ts.getPageInfo(area)

            while(driver.find_element_by_xpath("//li[contains(@class,'current')]/following-sibling::li").get_attribute("class") != "next"):
                driver.execute_script("arguments[0].click();",driver.find_element_by_xpath("//li[contains(@class,'next')]/a"))
                retstr += ts.getPageInfo(area)

            driver.quit()
        except NoSuchElementException as e:
            logger.warning(traceback.format_exc())
            driver.close()
            return traceback.format_exc()
        except Exception as e:
            logger.warning(traceback.format_exc())
            driver.close()
            return traceback.format_exc()

        logger.debug(retstr)
        return retstr

    def getPageInfo(ts,area):
        befhref = ""
        retstr = ""

        logger.debug("★" + driver.find_element_by_xpath("//li[contains(@class,'current')]/a").get_attribute("innerText") + "    " + driver.current_url)
        links = driver.find_elements_by_xpath("//a[contains(@class,'entry-title-link')]")
        
        for w in links:
            title = w.get_attribute("innerText")
            r = re.search("^(.+)さん[がの]?([^【】]+)(【(.+)】)?", title)
            if(r is None):
                r = re.search("^([^【】]+)[がの]([^【】]+)(【(.+)】)?", title)
            person = r.group(1)
            reason = r.group(2)
            tvprogram = r.group(4)

            if(tvprogram is None):
                tvprogram = ""

            # if(r.group(3) is not None):
            #     tvprogram = r.group(3)
            # else:
            #     tvprogram = ""
            logger.debug("#" + str(tvprogram))
            href = w.get_attribute("href")

            retstr += "\n▼[番組]" + tvprogram + "  [タレント]" + person + "   " + reason

            driver.execute_script("window.open()")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(href)

            tabelogs = driver.find_elements_by_xpath("//a[contains(@href,'https://tabelog.com/') and contains(@class,'blog-card-title-link')]")

            for w2 in tabelogs:
                if(befhref != w2.get_attribute("href")):
                    if(re.search(area, w2.get_attribute("innerText"))):
                        retstr += "\n　・" + w2.get_attribute("innerText") + "\n　　" + w2.get_attribute("href")

                befhref = w2.get_attribute("href")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        return retstr

    def getCurrentUrl(ts):
        return ts.curl

if __name__ == "__main__":
    xyzobj = XyzSearcher()
    # xyzobj.getCategory()
    # print(xyzobj.createCategoryString())
    print(xyzobj.searchList("銀座", "200"))
    print(xyzobj.getCurrentUrl())