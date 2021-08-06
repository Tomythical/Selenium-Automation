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

nine_am = 'start9_0'
one_pm = 'start13_0'
five_pm = 'start17_0'
six_pm = 'start18_0'

def get_time():
    now = date.today()
    # new_delta = now + timedelta(days=4)
    now2 = now.strftime("%d")
    new_delta2 = int(now2) + 5
    print(new_delta2)
    return(str(new_delta2))

def get_day():
    today = date.today().weekday()
    print(today)
    return today


def billyb(booking_time):
    driver.get("https://apps.dur.ac.uk/bookings/book/time")
    wait('username')
    driver.find_element_by_id('username').send_keys(username)
    time.sleep(1)
    driver.find_element_by_id ('password').send_keys(password)
    driver.find_element_by_xpath('//*[@id="content"]/div/div/form/button').click()
    wait('category_2')
    driver.find_element_by_id ('category_2').click()
    driver.find_element_by_id ('category_6').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/form/div/div[2]/div[3]/button').click()
    wait('date')
    driver.find_element_by_xpath('//*[@id="date"]').click()
    driver.find_element_by_xpath('//*[@id="date"]').send_keys(get_time())
    driver.find_element_by_xpath('//*[@id="type"]/option[2]').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[3]/form/div/button').click()
    wait('room6')
    driver.find_element_by_id ('room6').click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[4]/form/div/button').click()
    wait(booking_time)
    while True:
        if len(driver.find_elements_by_id(booking_time)) != 0:
            break
        else:
            # time.sleep(15)
            # driver.get("https://apps.dur.ac.uk/bookings/book/time")
            print("No time slot availiable")
            driver.close()
    driver.find_element_by_id(booking_time).click()
    driver.find_element_by_xpath('//*[@id="content"]/div/div/div[5]/form/div/button').click()
    wait('terms')
    while True:
        driver.find_element_by_id ('terms').click()
        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[6]/form/div/button').click()
        wait('terms')

def tlc(booking_time):
    driver.get("https://apps.dur.ac.uk/bookings/book/time")
    driver.execute_script("window.open('');")
    driver.find_element_by_id('username').send_keys('hdww72')
    time.sleep(1)
    driver.find_element_by_id ('password').send_keys('Fitirbit12')
    driver.find_element_by_xpath('//*[@id="content"]/div/div/form/button').click()
    wait('//*[@id="content"]/div/div/form/button')
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
    while True:
        driver.find_element_by_id ('terms').click()
        driver.find_element_by_xpath('//*[@id="content"]/div/div/div[6]/form/div/button').click()
        timeout = 60
        try:
            element_present = EC.presence_of_element_located((By.ID, 'terms'))
            WebDriverWait(driver, timeout).until(element_present)
        except TimeoutException:
            print("Timed out waiting for page to load")


def wait(id):
    timeout = 60
    try:
        element_present = EC.presence_of_element_located((By.ID, id))
        WebDriverWait(driver, timeout).until(element_present)
    except TimeoutException:
        print("Timed out waiting for page to load")

# if get_day() == 1 or get_day() == 2:
#     tlc(one_pm)
# else:
billyb(one_pm)




