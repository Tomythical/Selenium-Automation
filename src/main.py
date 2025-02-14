import argparse
import os
import sys
import time
from datetime import time as t

from dotenv import load_dotenv
from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import utils
from components import BrowserComponents

load_dotenv()
URL = "https://nsmembers.sswimclub.org.sg/group/pages/book-a-facility"

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")

LOADING_CLASS_NAME = "logo"

LOGIN_USERNAME_NAME = "_com_liferay_login_web_portlet_LoginPortlet_login"
LOGIN_PASSWORD_NAME = "_com_liferay_login_web_portlet_LoginPortlet_password"
LOGIN_SUBMIT_BUTTON_XPATH = (
    "//button[contains(@id, '_com_liferay_login_web_portlet_LoginPortlet_')]"
)
# DATE_PICKER_XPATH = "//input[contains(@id, '_activities_WAR_northstarportlet_:activityForm:j_idt65_input')]"
NEXT_WEEK_BUTTON_XPATH = (
    "//*[@id='_activities_WAR_northstarportlet_:activityForm:j_idt100']"
)

PREVIOUS_WEEK_BUTTON_XPATH = (
    "//*[@id='_activities_WAR_northstarportlet_:activityForm:j_idt79']"
)

NEXT_DAY_BUTTON_XPATH = (
    "//*[@id='_activities_WAR_northstarportlet_:activityForm:j_idt102']"
)


CLOCK_ID = "_activities_WAR_northstarportlet_\:activityForm\:j_idt70"

TABLE_ID = "_activities_WAR_northstarportlet_\:activityForm\:slots_data"

BOOKING_BUTTON_ID = "_activities_WAR_northstarportlet_\:activityForm\:j_idt1196"

UNAVAILABLE_BOOKING_OVERLAY = "advance-booking-overlay"

logger.remove(0)
logger.add(sys.stderr, level="DEBUG")


def argparser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "start_time", type=int, help="The start time of the booking in 24hr format"
    )
    parser.add_argument("-d", "--dry", action="store_true", help="Dry-Run")
    parser.add_argument(
        "-s", "--skip", action="store_true", help="Skip Booking Next Day"
    )

    args = parser.parse_args()
    return args.start_time, args.dry, args.skip


def login():
    browserComponents.waitForElementToDisappear(By.CLASS_NAME, LOADING_CLASS_NAME, 30)
    browserComponents.waitForElementToBeVisible(By.NAME, LOGIN_USERNAME_NAME, 30)

    logger.debug("Logging in")
    browserComponents.findInputAndSendKeys(By.NAME, LOGIN_USERNAME_NAME, USERNAME)
    time.sleep(0.5)
    browserComponents.findInputAndSendKeys(By.NAME, LOGIN_PASSWORD_NAME, PASSWORD)

    browserComponents.waitForElementToBeClickable(
        By.XPATH, LOGIN_SUBMIT_BUTTON_XPATH, 5
    )
    browserComponents.findElementAndClick(By.XPATH, LOGIN_SUBMIT_BUTTON_XPATH)


def navigate_to_date(skip_next_day, dry_run):
    browserComponents.waitForElementToDisappear(By.CLASS_NAME, LOADING_CLASS_NAME, 20)
    browserComponents.waitForElementToBeClickable(By.XPATH, NEXT_WEEK_BUTTON_XPATH, 20)

    logger.info("Clicking Next Week")

    next_week_not_available = True
    while next_week_not_available:
        try:
            browserComponents.findElementAndClick(By.XPATH, NEXT_WEEK_BUTTON_XPATH)
            next_week_not_available = False
        except ElementClickInterceptedException:
            time.sleep(1)

    while browserComponents.findElementAndGetText(By.ID, CLOCK_ID) == "":
        time.sleep(1)

    wait_time = 0
    while True:
        try:
            clock_text = browserComponents.findElementAndGetText(By.ID, CLOCK_ID)
        except StaleElementReferenceException as e:
            logger.warning(f"Stale element trying to get clock time. {e}")
            time.sleep(1)
            wait_time += 1
            continue

        if clock_text == "":
            time.sleep(1)
            wait_time += 1
            continue

        clock_datetime = utils.parse_server_clock(clock_text)
        if dry_run:
            clock_datetime = t(7, 0)

        if t(7, 0) <= clock_datetime <= t(7, 59):  # If after midnight
            logger.info(f"It is now past midnight: {clock_datetime}")
            break

        if wait_time >= 180:
            logger.info("Did not pass midnight after 3 minutes")
            driver.quit()
            exit(1)

        logger.debug(f"Local time: {clock_datetime}. Wait time = {wait_time}")
        time.sleep(1)
        wait_time += 1

    if skip_next_day or dry_run:
        return

    # logger.info("Clicking Next Day")
    # browserComponents.waitForElementToBeClickable(By.XPATH, NEXT_DAY_BUTTON_XPATH, 20)
    # time.sleep(2)
    # browserComponents.findElementAndClick(By.XPATH, NEXT_DAY_BUTTON_XPATH)
    # time.sleep(2)

    attempts = 0
    while (
        browserComponents.isElementPresent(By.CLASS_NAME, UNAVAILABLE_BOOKING_OVERLAY)
        and attempts < 3
    ):
        logger.debug(f"{attempts=}")
        logger.debug("Booking screen unavailable")
        browserComponents.waitForElementToBeClickable(
            By.XPATH, PREVIOUS_WEEK_BUTTON_XPATH, 20
        )
        browserComponents.findElementAndClick(By.XPATH, PREVIOUS_WEEK_BUTTON_XPATH)
        time.sleep(2)
        browserComponents.waitForElementToBeClickable(
            By.XPATH, NEXT_WEEK_BUTTON_XPATH, 20
        )
        browserComponents.findElementAndClick(By.XPATH, NEXT_WEEK_BUTTON_XPATH)
        time.sleep(2)
        attempts += 1

    if attempts >= 3:
        logger.info("Booking screen never went away")
        driver.quit()
        exit(1)


def choose_court():
    logger.info("Choosing Court")
    time.sleep(1)
    driver.execute_script("window.scrollBy(0, 500);")
    time.sleep(1)
    tableRow = start_time - 7
    courtElements = browserComponents.getElementsInRow(TABLE_ID, tableRow)
    preference_order = (4, 5, 3, 1, 2, 6)
    for court in preference_order:
        try:
            if courtElements[court].text != "":
                logger.debug(
                    f"Court {court} is not available: {courtElements[court].text}"
                )
            else:
                logger.debug(f"Court {court} is available")
                try:
                    logger.debug(f"Clicking table id: t{tableRow}c{court-1}")
                    browserComponents.waitForElementToBeClickable(
                        By.ID, f"t{tableRow}c{court-1}", 5
                    )
                    browserComponents.findElementAndClick(
                        By.ID, f"t{tableRow}c{court-1}"
                    )
                    return
                except ElementNotInteractableException:
                    logger.warning(f"Court {court} has no clickable element")
                except TimeoutException:
                    logger.warning(f"Timeout: Court {court} is not available")
                except ElementClickInterceptedException as e:
                    logger.warning(f"Element click intercepted: {e}")
        except IndexError:
            logger.warning(f"IndexError: Court {court} is not available")

    logger.error("No courts available")
    logger.info("Quitting driver")
    driver.quit()
    exit(1)


def book_court():
    time.sleep(1)
    browserComponents.waitForElementToDisappear(By.CLASS_NAME, LOADING_CLASS_NAME, 10)
    browserComponents.waitForElementToBeClickable(By.ID, BOOKING_BUTTON_ID, 10)
    if not dry_run:
        logger.info(f"Booking court")
        browserComponents.findElementAndClick(By.ID, BOOKING_BUTTON_ID)
        browserComponents.waitForElementToDisappear(By.ID, LOADING_CLASS_NAME, 10)
        browserComponents.waitForElementToBeVisible(
            By.XPATH, NEXT_WEEK_BUTTON_XPATH, 30
        )
        logger.info("Booking complete")
    else:
        logger.debug("Reached booking screen. Not booking court")


if __name__ == "__main__":
    start_time, dry_run, skip_next_day = argparser()

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    browserComponents = BrowserComponents(driver)
    driver.maximize_window()
    driver.get(URL)
    login()
    navigate_to_date(skip_next_day, dry_run)
    choose_court()
    book_court()

    logger.info("Booking Finished")
