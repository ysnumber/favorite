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
import gspread

import logging
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = logging.FileHandler("GMap.log", mode='a', encoding='utf-8')
handler.setLevel(DEBUG)
handler.setFormatter(logging.Formatter('%(asctime)s    %(message)s'))
logger.setLevel(DEBUG)
logger.addHandler(handler)
logger.propagate = False

chrome_mode="headless"
# chrome_mode=""
driver=None
max_row = 3

class GMapSearcher():

    def __init__(self):
        self.curl = ""
        self.catlist = []
        self.wks = None
        self.rcnt = 1

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



    def searchList(self):
        global driver
        retstr = ""
        cnt = 0

        try:
            self.getDriver()

            driver.get("https://www.google.com/maps/d/u/0/edit?hl=ja&mid=1IiT4Tc17Nl6pBTzbkEw6nZLG7gbrKRwD")
            
            self.curl = driver.current_url
            list = driver.find_elements_by_xpath("//div[@class='suEOdc']")

            self.openSpread()

            for w in list:
                if(cnt == 0):
                    cnt = cnt + 1
                    continue

                # if(max_row < cnt):
                #     break
                driver.execute_script("arguments[0].click();",w)
                # WebDriverWait(driver, 2).until(EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'fO2voc-jRmmHf-MZArnb-Q7Zjwb')]")))
                sleep(1)

                address = self.getWebElementByXpathObject(driver, "//div[contains(@class,'fO2voc-jRmmHf-MZArnb-Q7Zjwb')]")
                if(address is not None):
                    address = address.get_attribute("innerText")
                else: address = ""
                descript = self.getWebElementByXpathObject(driver, "//div[contains(@class,'qqvbed-p83tee-V1ur5d') and text()='説明']/following-sibling::div")
                if(descript is not None):
                    descript = descript.get_attribute("innerText")
                else: descript = ""

                link = self.getWebElementByXpathObject(driver, "//div[contains(@class,'fO2voc-jRmmHf-LJTIlf')]//a[contains(@href,'http') and not(contains(@href,'https://www.google.com'))]")
                # link = self.getWebElementByXpathObject(linkParent, "//a[contains(@href,'http') and not(contains(@href,'https://www.google.com'))]")
                if(link is not None):
                    link = link.get_attribute("href")
                else: link = ""

                self.wks.update_acell("A" + str(self.rcnt), w.get_attribute("innerText"))
                self.wks.update_acell("B" + str(self.rcnt), address)
                self.wks.update_acell("C" + str(self.rcnt), descript)
                self.wks.update_acell("D" + str(self.rcnt), link)
                self.rcnt = self.rcnt + 1
                sleep(5)

                cnt = cnt + 1
                

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

    def openSpread(self):
        scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
        credentials = ServiceAccountCredentials.from_json_keyfile_name('./WebTrainProject-a52aed0e9fb4.json', scope)
        gc = gspread.authorize(credentials)
        self.wks = gc.open("GoogleMapToraArround").sheet1
        self.wks.clear()


    def getWebElementByXpathObject(self, target, xpath):
        if(target is None):
            return None
        try:
            return target.find_element_by_xpath(xpath)
        except NoSuchElementException:
            return None

    def getCurrentUrl(self):
        return self.curl

if __name__ == "__main__":
    xyzobj = GMapSearcher()
    # xyzobj.getCategory()
    # print(xyzobj.createCategoryString())
    print(xyzobj.searchList())
    print(xyzobj.getCurrentUrl())