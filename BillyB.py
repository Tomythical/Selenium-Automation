
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from datetime import date, timedelta
from selenium.webdriver.common.keys import Keys
from Passwords import username,password

driver = webdriver.Safari()

nine_am = 'start9_0'
one_pm = 'start13_0'
five_pm = 'start17_0'
six_pm = 'start18_0'

def get_time():
    now = date.today()
    new_delta = now + timedelta(days=4)
    print(new_delta)
    return(str(new_delta))

def get_day():
    today = date.today().weekday()
    print(today)
    return today


def billyb(booking_time):
    driver.get("https://apps.dur.ac.uk/bookings/book/time")
    time.sleep(2)
    driver.find_element_by_id('username').send_keys(username)
    driver.find_element_by_id ('password').send_keys(password)
    driver.find_element_by_xpath('//*[@id="content"]/div/div/form/button').click()
    time.sleep(4)
    driver.find_element_by_id ('category_2').click()
    driver.find_element_by_id ('category_6').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/form/div/div[2]/div[3]/button').click()
    time.sleep(4)
    driver.find_element_by_xpath('//*[@id="date"]').clear()
    driver.find_element_by_xpath('//*[@id="date"]').send_keys(get_time())
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[3]/form/div/button').click()
    time.sleep(4)
    driver.find_element_by_id ('room6').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[4]/form/div/button').click()
    time.sleep(4)
    while True:
        if len(driver.find_elements_by_id(booking_time)) != 0:
            break
        else:
            time.sleep(2)
            driver.get("https://apps.dur.ac.uk/bookings/book/time")
    driver.find_element_by_id(booking_time).click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[5]/form/div/button').click()
    time.sleep(5)
    driver.find_element_by_id ('terms').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[6]/form/div/button').click()
    time.sleep(5)

def tlc(booking_time):
    driver.get("https://apps.dur.ac.uk/bookings/book/time")
    driver.execute_script("window.open('');")
    driver.find_element_by_id('username').send_keys('hdww72')
    time.sleep(1)
    driver.find_element_by_id ('password').send_keys('Fitirbit12')
    driver.find_element_by_xpath('//*[@id="content"]/div/div/form/button').click()
    time.sleep(4)
    driver.find_element_by_id ('category_2').click()
    driver.find_element_by_id ('category_6').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/form/div/div[2]/div[3]/button').click()
    time.sleep(4)
    driver.find_element_by_xpath('//*[@id="date"]').clear()
    driver.find_element_by_xpath('//*[@id="date"]').send_keys(get_time())
    se = Select(driver.find_element_by_id('type'))
    se.select_by_value('6')
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[3]/form/div/button').click()
    time.sleep(4)
    driver.find_element_by_id ('room26').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[4]/form/div/button').click()
    time.sleep(4)
    while True:
        if len(driver.find_elements_by_id(booking_time)) != 0:
            break
        else:
            time.sleep(2)
            driver.get("https://apps.dur.ac.uk/bookings/book/time")
    driver.find_element_by_id(booking_time).click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[5]/form/div/button').click()
    time.sleep(5)
    driver.find_element_by_id ('terms').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[6]/form/div/button').click()
    time.sleep(5)



if get_day() == 1 or get_day() == 2:
    tlc(one_pm)
else:
    billyb(one_pm)



