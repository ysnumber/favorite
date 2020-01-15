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
    
    def searchList(ts, erea, cat):
        global driver
        befhref = ""
        retstr = ""

        ts.getDriver()

        driver.get("http://xn--qck4e3a468yfxr0q3azkrifd985b.xyz/?s=" + erea + "&cat=" + cat)

        links = driver.find_elements_by_xpath("//a[contains(@class,'entry-title-link')]")
        
        for w in links:
            title = w.get_attribute("innerText")
            r = re.search("^(.+)さん[がの]?(.+)【(.+)】", title)
            person = r.group(1)
            reason = r.group(2)
            tvprogram = r.group(3)
            href = w.get_attribute("href")

            retstr += "\n番組:" + tvprogram + "  タレント：" + person + "   " + reason

            driver.execute_script("window.open()")
            driver.switch_to.window(driver.window_handles[1])
            driver.get(href)

            tabelogs = driver.find_elements_by_xpath("//a[contains(@href,'https://tabelog.com/')]")

            for w2 in tabelogs:
                if(befhref != w2.get_attribute("href")):
                    retstr += "\n" + w2.get_attribute("href")

                befhref = w2.get_attribute("href")

            driver.close()
            driver.switch_to.window(driver.window_handles[0])

        driver.close()
        return retstr


if __name__ == "__main__":
    xyzobj = XyzSearcher()
    # xyzobj.getCategory()
    # print(xyzobj.createCategoryString())
    print(xyzobj.searchList("銀座", "200"))