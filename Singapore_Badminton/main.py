import argparse
import os
import sys
import time
from datetime import datetime, timedelta

import pretty_errors
from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ActionChains
from pyvirtualdisplay import Display
from components import BrowserComponents


load_dotenv()
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

LOGIN_USERNAME_NAME = "txtMemberID"
LOGIN_PASSWORD_NAME = "txtPassWord"
LOGIN_SUBMIT_BUTTON_NAME = "Submit1"

BOOKING_FACILITY_LINK = "Booking of Facility"
BADMINTON_BKG_LINK = "BADMINTON BKG"

BOOK_NOW_BUTTON_ID = "submit1"

EMAIL_INPUT_ID = "txtEmail"

logger.remove(0)
logger.add(sys.stderr, level="ERROR")

display = Display(visible=0, size=(800, 600))
display.start()

def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start_time", type=int, help="The start time of the booking in 24hr format"
    )
    parser.add_argument(
        "--email", type=str, help="The email required for the booking confirmation"
    )
    args = parser.parse_args()
    return args.start_time, args.email


def login():
    logger.debug("Logging in")
    browserComponents.waitForElementToBeVisible(By.NAME, LOGIN_USERNAME_NAME, 10)
    browserComponents.findInputAndSendKeys(By.NAME, LOGIN_USERNAME_NAME, USERNAME)
    time.sleep(1)
    browserComponents.findInputAndSendKeys(By.NAME, LOGIN_PASSWORD_NAME, PASSWORD)
    browserComponents.findElementAndClick(By.ID, LOGIN_SUBMIT_BUTTON_NAME)


def navigateToBookingPage():
    logger.debug("Clicking Booking Facility Link")
    browserComponents.waitForElementToBeVisible(By.LINK_TEXT, BOOKING_FACILITY_LINK, 3)
    browserComponents.findElementAndClick(By.LINK_TEXT, BOOKING_FACILITY_LINK)

    logger.debug("Clicking Badminton Bkg")
    browserComponents.waitForElementToBeVisible(By.LINK_TEXT, BADMINTON_BKG_LINK, 3)
    browserComponents.findElementAndClick(By.LINK_TEXT, BADMINTON_BKG_LINK)

    localcurrentdateandtime = datetime.now()
    currentDay = localcurrentdateandtime.strftime("%d")
    nextWeekDate = int(currentDay) + 7
    logger.debug(f"Next week date : {nextWeekDate}")

    browserComponents.waitForElementToBeVisible(By.LINK_TEXT, str(nextWeekDate), 2)
    browserComponents.findElementAndClick(By.LINK_TEXT, str(nextWeekDate))


def choose_court(start_time):
    logger.info("Choosing Court")
    browserComponents.waitForElementToBeVisible(By.ID, BOOK_NOW_BUTTON_ID, 2)
    courtElements7am = browserComponents.getElementsInRow("Table3", start_time - 6)
    preference_order = (4, 5, 3, 1, 2, 6)
    for court in preference_order:
        logger.debug(f"Court {court}: {courtElements7am[court].text}")
        if courtElements7am[court].text == "Available":
            return court

    logger.error("No courts available")
    logger.info("Quitting driver")
    driver.quit()
    exit(1)


def choose_time_and_submit(start_time: int, court: int):
    todayDate = datetime.now() + timedelta(weeks=1)
    todayDateFormatted = todayDate.strftime("%d %b %Y")
    BOOKING_TABLE_CHECKBOX_VALUE = f"{str(start_time).zfill(2)}:00,{str(start_time+1).zfill(2)}:00,BC{str(court)},{todayDateFormatted},B"

    browserComponents.findInputByAttributeAndClick(
        "value", BOOKING_TABLE_CHECKBOX_VALUE
    )

    logger.debug(f"Clicking Checkbox: {BOOKING_TABLE_CHECKBOX_VALUE}")
    browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)


def enter_email_and_book(email):
    logger.debug(f"Sending email: {email} and booking")
    browserComponents.waitForElementToBeVisible(By.ID, EMAIL_INPUT_ID, 5)
    browserComponents.findInputAndSendKeys(By.ID, EMAIL_INPUT_ID, email)
    # browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)

    time.sleep(5)

if __name__ == "__main__":
    start_time, email = argparser()

    options = Options()
    options.add_argument('--headless')

    driver = webdriver.Chrome(options=options)
    browserComponents = BrowserComponents(driver)
    driver.maximize_window()
    driver.get("https://www.sswimclub.org.sg/MembersWeb/main/loginuser.asp")

    login()
    navigateToBookingPage()
    court = choose_court(start_time)
    choose_time_and_submit(start_time, court)
    enter_email_and_book(email)
