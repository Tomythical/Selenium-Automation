from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from datetime import date, timedelta, datetime
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from Passwords import username,password

driver = webdriver.Safari()

url = 'https://durhamuni.xncloud.co.uk/LhWeb/en/Members/home'

driver.get(url)
driver.implicitly_wait(10)
driver.find_element_by_class_name('xn-button xn-cta').click()
action = webdriver.common.action_chains.ActionChains(driver)
action.move_to_element_with_offset(el, 5, 5)
action.click()
action.perform()
# driver.find_element_by_xpath('//*[@id="K3TULGJ35S96A350Y1R35ELHTJ7EGCGI"]/xn-cookiebanner-component/div/div/div[2]/button').click()