from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import json
import time
import os.path
import re

baseUrl = 'https://bscscan.com'


def getAllLabels():
    driver.get(baseUrl + '/labelcloud')
    driver.implicitly_wait(5)

    elems = driver.find_elements("class name", "d-block")
    labels = []
    labelIndex = len(baseUrl + '/accounts/label/')
    for elem in elems:
        href = elem.get_attribute("href")
        print(href, '/ Text:', elem.text)

    print(labels)
    print('L:', len(labels))


if __name__ == '__main__':
    driver = webdriver.Chrome(service=ChromeService(
        ChromeDriverManager().install()))
    getAllLabels()

    driver.quit()
