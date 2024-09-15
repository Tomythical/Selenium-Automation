import argparse
import os
import sys
import time
from datetime import datetime, timedelta

import pytz
from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from components import BrowserComponents

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
PRINT_THIS_PAGE_LINK = "Click to Print This Page"

singapore_timezone = pytz.timezone("Asia/Singapore")
singapore_currentdateandtime = datetime.now(singapore_timezone)
singapore_date_plus_7_days = (
    singapore_currentdateandtime + timedelta(days=7)
).strftime("%-d %b %Y")

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

    currentDay = singapore_currentdateandtime.strftime("%-d")
    logger.debug(f"Today's date in Singapore: {currentDay}")

    browserComponents.waitForElementToBeVisible(By.LINK_TEXT, str(currentDay), 2)
    browserComponents.findElementAndClick(By.LINK_TEXT, str(currentDay))


def choose_date_and_court(start_time):
    logger.info("Choosing date from dropdown")
    browserComponents.waitForElementToBeVisible(By.ID, BOOK_NOW_BUTTON_ID, 2)
    browserComponents.findElementAndClick(By.NAME, DATE_PICKER_NAME)

    singapore_currentdateandtime = datetime.now(singapore_timezone)
    logger.debug(f"Date in Singapore: {singapore_currentdateandtime}")
    logger.debug(f"7 days ahead from Singapore: {singapore_date_plus_7_days}")

    # logger.debug("Sleeping for 30 seconds")
    # time.sleep(30)

    logger.info(f" Attempting to click date: {singapore_date_plus_7_days}")
    wait_time = 0

    while str(singapore_currentdateandtime.strftime("%H")) != "07":
        logger.debug(
            f"Time: {singapore_currentdateandtime.strftime('%H:%M:%S')}. Wait time = {wait_time}"
        )
        if wait_time == 120:
            logger.info("Date not found after 2 minutes")
            driver.quit()
            exit(1)

        time.sleep(1)
        singapore_currentdateandtime = datetime.now(singapore_timezone)
        wait_time += 1

    driver.refresh()
    browserComponents.waitForElementToBeVisible(By.ID, BOOK_NOW_BUTTON_ID, 2)
    browserComponents.findElementAndClick(By.NAME, DATE_PICKER_NAME)
    browserComponents.findElementByAttributeAndClick(
        "option", "value", singapore_date_plus_7_days
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
    nextWeekDate = singapore_currentdateandtime + timedelta(weeks=1)
    nextWeekFormatted = nextWeekDate.strftime("%-d %b %Y")
    BOOKING_TABLE_CHECKBOX_VALUE = f"{str(start_time).zfill(2)}:00,{str(start_time+1).zfill(2)}:00,BC{str(court)},{nextWeekFormatted},B"

    browserComponents.findElementByAttributeAndClick(
        "input", "value", BOOKING_TABLE_CHECKBOX_VALUE
    )

    logger.debug(f"Clicking Checkbox: {BOOKING_TABLE_CHECKBOX_VALUE}")
    browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)


def enter_email_and_book(email, dry_run):
    browserComponents.waitForElementToBeVisible(By.ID, EMAIL_INPUT_ID, 5)
    browserComponents.findInputAndSendKeys(By.ID, EMAIL_INPUT_ID, email)
    if not dry_run:
        logger.info(f"Sending email: {email} and booking")
        browserComponents.findElementAndClick(By.ID, BOOK_NOW_BUTTON_ID)
        browserComponents.waitForElementToBeVisible(
            By.LINK_TEXT, PRINT_THIS_PAGE_LINK, 120
        )
        logger.info("Booking complete")
    else:
        logger.debug("Reached email screen. Not sending email")


if __name__ == "__main__":
    start_time, email, dry_run = argparser()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browserComponents = BrowserComponents(driver)
    driver.maximize_window()
    driver.get(
        "https://membership.sswimclub.org.sg/MembersWeb/main/loginuser.asp?errmsg=2"
    )

    login()
    navigateToBookingPage()
    court = choose_date_and_court(start_time)
    choose_time_and_submit(start_time, court)
    enter_email_and_book(email, dry_run)
    logger.info("Booking Finished")
