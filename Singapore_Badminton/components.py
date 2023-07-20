from loguru import logger
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


class BrowserComponents:
    def __init__(self, webDriver) -> None:
        self.driver = webDriver

    def waitForElementToBeVisible(self, locator_type: By, locator: str, timeout: int):
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located((locator_type, locator))
            )
        except NoSuchElementException:
            logger.error(
                f"Locator: {locator} could not be found using locator type: {locator_type}"
            )
            self.driver.quit()

    def findInputAndSendKeys(self, locator_type: By, locator: str, message: str):
        try:
            self.driver.find_element(locator_type, locator).send_keys(message)
        except NoSuchElementException:
            logger.error(
                f"Locator: {locator} could not be found using locator type: {locator_type}"
            )
            self.driver.quit()

    def findElementAndClick(self, locator_type: By, locator: str):
        try:
            self.driver.find_element(locator_type, locator).click()
        except NoSuchElementException:
            logger.error(
                f"Locator: {locator} could not be found using locator type: {locator_type}"
            )
            self.driver.quit()

    def findElementFromElementsThroughAttributeAndClick(
        self, locator_type: By, locator: str, element: str, attribute: str
    ):
        try:
            elements = self.driver.find_elements(locator_type, locator)
            for e in elements:
                if e.get_attribute(attribute) == element:
                    e.click()
                    break
            else:
                logger.error(
                    f"No match found for element: {element} using locator: {locator}"
                )
                self.driver.quit()

        except NoSuchElementException:
            print(
                f"Locators: {locator} could not be found using attribute type: {attribute}"
            )
            self.driver.quit()

    def findInputByAttributeAndClick(self, attribute: str, value: str):
        try:
            self.driver.find_element(
                By.XPATH, f"//input[@{attribute}='{value}']"
            ).click()
        except NoSuchElementException:
            logger.error(
                f"Element could not be found using attribute: {attribute}, for value: {value}"
            )
            self.driver.quit()

    def findElementsMatchingText(self, locator_type: By, locator: str, text: str):
        try:
            elements = self.driver.find_elements(locator_type, locator)
            element_list = []
            for e in elements:
                if e.text() == text:
                    element_list.append(element_list)

            if len(element_list) == 0:
                logger.error(
                    f"No elements of locator: {locator}, matching text: {text}"
                )
                self.driver.quit()

            return element_list
        except NoSuchElementException:
            logger.error(
                f"Locators {locator} could not be found using locator type: {locator}"
            )
            self.driver.quit()

    def getElementsInRow(self, table_id: str, row_num: int):
        try:
            table_id = self.driver.find_element(By.ID, table_id)
            rows = table_id.find_elements(By.TAG_NAME, "tr")
            row = rows[row_num]
            columnElements = row.find_elements(By.TAG_NAME, "td")
            return columnElements
        except NoSuchElementException as err:
            logger.error(err)
            self.driver.quit()
