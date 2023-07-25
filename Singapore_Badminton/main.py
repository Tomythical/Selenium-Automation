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
from selenium.webdriver.safari.options import Options

from components import BrowserComponents

options = Options()
options.add_argument("--disable-blink-features=AutomationControlled")

load_dotenv()
USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

LOGIN_USERNAME_NAME = "txtMemberID"
LOGIN_PASSWORD_NAME = "txtPassWord"
LOGIN_SUBMIT_BUTTON_NAME = "Submit1"

BOOKING_FACILITY_LINK = "Booking of Facility"
BADMINTON_BKG_LINK = "BADMINTON BKG"

DATE_PICKER_NAME = "dday"
BOOK_NOW_BUTTON_ID = "submit1"

EMAIL_INPUT_ID = "txtEmail"

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start_time", type=int, help="The start time of the booking in 24hr format"
    )
    parser.add_argument(
        "--email", type=str, help="The email required for the booking confirmation"
    )
    parser.add_argument("-d", "--dry", action="store_true", help="Dry-Run")
    args = parser.parse_args()
    return args.start_time, args.email, args.dry


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

    singapore_currentdateandtime = datetime.now() + timedelta(hours=7)
    currentDay = singapore_currentdateandtime.strftime("%-d")
    logger.debug(f"Today's date in Singapore: {currentDay}")

    browserComponents.waitForElementToBeVisible(By.LINK_TEXT, str(currentDay), 2)
    browserComponents.findElementAndClick(By.LINK_TEXT, str(currentDay))


def choose_date_and_court(start_time):
    logger.info("Choosing date from dropdown")
    browserComponents.waitForElementToBeVisible(By.ID, BOOK_NOW_BUTTON_ID, 2)
    browserComponents.findElementAndClick(By.NAME, DATE_PICKER_NAME)
    sixDaysDate = datetime.now() + timedelta(days=6)
    nextWeekDate = datetime.now() + timedelta(weeks=1)

    sixDaysDateFormatted = sixDaysDate.strftime("%-d %b %Y")
    nextWeekDateFormatted = nextWeekDate.strftime("%-d %b %Y")

    logger.debug(f"6 days ahead: {sixDaysDateFormatted}")
    logger.debug(f"Next week: {nextWeekDateFormatted}")
    logger.info(f"Clicking date: {nextWeekDateFormatted}")
    browserComponents.findElementByAttributeAndClick(
        "option", "value", nextWeekDateFormatted
    )
    browserComponents.waitForElementToBeVisible(By.ID, BOOK_NOW_BUTTON_ID, 2)

    logger.info("Choosing Court")
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
    newtWeekDate = datetime.now() + timedelta(weeks=1)
    nextWeekFormatted = newtWeekDate.strftime("%-d %b %Y")
    BOOKING_TABLE_CHECKBOX_VALUE = f"{str(start_time).zfill(2)}:00,{str(start_time+1).zfill(2)}:00,BC{str(court)},{nextWeekFormatted},B"

    browserComponents.findElementByAttributeAndClick(
        "input", "value", BOOKING_TABLE_CHECKBOX_VALUE
    )

    logger.debug(f"Clicking Checkbox: {BOOKING_TABLE_CHECKBOX_VALUE}")
    browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)


def enter_email_and_book(email, dry_run):
    logger.debug(f"Sending email: {email} and booking")
    browserComponents.waitForElementToBeVisible(By.ID, EMAIL_INPUT_ID, 5)
    browserComponents.findInputAndSendKeys(By.ID, EMAIL_INPUT_ID, email)
    if not dry_run:
        browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)


if __name__ == "__main__":
    start_time, email, dry_run = argparser()

    driver = webdriver.Chrome()
    browserComponents = BrowserComponents(driver)
    driver.maximize_window()
    driver.get("https://www.sswimclub.org.sg/MembersWeb/main/loginuser.asp")
    login()
    navigateToBookingPage()
    court = choose_date_and_court(start_time)
    choose_time_and_submit(start_time, court)
    enter_email_and_book(email, dry_run)

    time.sleep(2)
