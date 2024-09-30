import time

from selenium import webdriver
from selenium.common import StaleElementReferenceException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.ie.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

URL = 'https://eu.idec.com/idec-eu/en_EU/media-center/press'
DIR = "/home/roberto/PycharmProjects/DataScrapers-pet-projects-/PDFscraper/data"
COOKIE_ID = 'CybotCookiebotDialogFooter'
COOKIE_BUTTON = 'CybotCookiebotDialogBodyLevelButtonLevelOptinAllowAll'

APP_DIV_ID = 'app'
CONTENT_DIV = 'div.outerWrapper'
TAG_NAME = 'a'


class PDFScraper:
    def __init__(self, url: str, download_dir: str):
        self.url = url
        self.download_dir = download_dir
        self.driver = self._setup_driver()
        self.used_links = set()

    def _setup_driver(self) -> WebDriver:
        """
        Setting Chromium options for specifying downloading directory,
        automatically downloading and opening pdf files.
        :return:
            Selenium driver type 'WebDriver'
        """
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_experimental_option('prefs', {
            'download.default_directory': self.download_dir,
            'download.prompt_for_download': False,
            'plugins.always_open_pdf_externally': True
        })
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
        return driver

    def _accept_cookies(self):
        """
        Handling all cookies stuff including deleting all history cookie,
        waiting for cookie to appear and accepting it.
        """
        try:
            self.driver.delete_all_cookies()
        except Exception:
            pass

        try:
            cookie_div = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, COOKIE_ID))
            )
            if cookie_div:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, COOKIE_BUTTON))).click()
        except Exception:
            print(f"Cookie consent not found or could not be clicked")

    def _get_pdf_links(self):
        """
        A simple generator for yielding every pdf we need,
        refreshing divs every time for handling errors with missing stales ,
        and clearing all staff.
        """
        while True:
            try:
                new_element_found = False
                WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, APP_DIV_ID)))
                app_div = self.driver.find_element(By.ID, APP_DIV_ID)
                content_div = app_div.find_element(By.CSS_SELECTOR, CONTENT_DIV)
                links = content_div.find_elements(By.TAG_NAME, TAG_NAME)
            except StaleElementReferenceException:
                continue

            for link in links:
                try:
                    href = link.get_attribute('href')
                    if href and link not in self.used_links and '.pdf' in href:
                        self.used_links.add(link)
                        yield link
                        new_element_found = True
                        break
                except StaleElementReferenceException:
                    continue
            if not new_element_found:
                self.used_links.clear()
                break

    def _download_pdfs(self):
        for link in self._get_pdf_links():
            try:
                WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable(link)).click()
            except StaleElementReferenceException:
                self.used_links.remove(link)
                continue

            except Exception as e:
                print(f"Error while downloading pdf - {e}")
                continue

    def scrape(self):
        self.driver.get(self.url)
        self.driver.maximize_window()
        self._accept_cookies()
        self._download_pdfs()

        print("Downloading in process... ")
        time.sleep(2)  # giving time for downloading all PDF
        print("Completed!")

        self.driver.quit()


if __name__ == "__main__":
    scraper = PDFScraper(URL, DIR)
    scraper.scrape()
