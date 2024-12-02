import pytest
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import pandas as pd


CSV_FILE_PATH = "test_results.csv"

class TestWordpressLogin:
    def setup_method(self, method):
        # Set up headless Chrome options for CI
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-infobars")
        chrome_options.add_argument("--disable-popup-blocking")
        chrome_options.add_argument("--disable-notifications")
        chrome_options.add_argument("--incognito")
        chrome_options.add_argument("window-size=1296,696")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.set_page_load_timeout(60)
        self.driver.set_script_timeout(30)
        self.driver.implicitly_wait(10)

        # Ensure screenshots directory exists
        if not os.path.exists("screenshots"):
            os.makedirs("screenshots")
        
        self.vars = {}
  
    def teardown_method(self, method):
        self.driver.quit()

    def append_to_csv(self, results):
        df = pd.DataFrame(results)
        if os.path.exists(CSV_FILE_PATH):
            df.to_csv(CSV_FILE_PATH, mode='a', header=False, index=False)
        else:
            df.to_csv(CSV_FILE_PATH, mode='w', header=True, index=False)
  
    def scroll_to_element(self, by, value):
        """Scroll incrementally until the element is in view and clickable."""
        for _ in range(15):  # Increase the number of scroll attempts
            try:
                element = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((by, value))
                )
                return element
            except:
                # Incrementally scroll down by 300px if the element is not yet clickable
                self.driver.execute_script("window.scrollBy(0, 300);")
                time.sleep(1)  # Pause briefly after each scroll
        raise Exception("Element not found or not clickable")

    def test_11Plus(self):
        # Start time to calculate test duration
        start_time = time.time()

        self.driver.get("https://smoothmaths.co.uk/login/")
        self.driver.find_element(By.ID, "user_login").send_keys("hanzila@dovidigital.com")
        self.driver.find_element(By.ID, "user_pass").send_keys("Hanzila*183258")
        self.driver.find_element(By.ID, "wp-submit").click()
        
        main_page_url = "https://smoothmaths.co.uk/igcse/edexcel/january-2014-maths-past-papers/"
        self.driver.get(main_page_url)

        expected_answers_urls = [
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper1f-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper1fr-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper2f-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper2fr-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper3h-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper3hr-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper4h-january2014.pdf",
            "https://smoothmaths.s3.eu-west-2.amazonaws.com/markscheme-paper4hr-january2014.pdf",
        ]

        answer_paper_locators = [
            (By.CSS_SELECTOR, ".et_pb_blurb_1.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_3.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_5.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_7.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_9.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_12.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_14.et_pb_blurb .et_pb_module_header a"),
            (By.CSS_SELECTOR, ".et_pb_blurb_17.et_pb_blurb .et_pb_module_header a"),
        ]

        results = []

        # Test each Answer Paper link
        for i, (by, value) in enumerate(answer_paper_locators):
            try:
                # Scroll to the element and get the clickable element
                answer_paper_link = self.scroll_to_element(by, value)
                answer_paper_link.click()

                # Switch to the newly opened tab
                WebDriverWait(self.driver, 5).until(lambda d: len(d.window_handles) > 1)
                self.driver.switch_to.window(self.driver.window_handles[1])

                # Wait for the page to fully load
                time.sleep(5)  # Adjust the sleep time if necessary

                # Verify the current URL
                WebDriverWait(self.driver, 15).until(EC.url_to_be(expected_answers_urls[i]))

                # Assert the URL is correct
                assert self.driver.current_url == expected_answers_urls[i], f"Expected URL to be {expected_answers_urls[i]}, but got {self.driver.current_url}"

                # Wait additional time for rendering and then take a screenshot
                time.sleep(3)  # Extra wait for rendering
                screenshot_path = f"screenshots/EdexcelJanuary2014Markscheme_{i+1}.png"
                self.driver.save_screenshot(screenshot_path)

                # Log success status
                results.append({
                    "Test Case": f"Answer Paper {i+1} Link Verification",
                    "Status": "Pass",
                    "Expected URL": expected_answers_urls[i],
                    "Actual URL": self.driver.current_url,
                    "Screenshot": screenshot_path
                })

                # Close the current tab and switch back to the main tab
                self.driver.close()
                self.driver.switch_to.window(self.driver.window_handles[0])

            except Exception as e:
                # Capture any errors and log failure status
                screenshot_path = f"screenshots/EdexcelJanuary2014Markscheme_error_{i+1}.png"
                self.driver.save_screenshot(screenshot_path)

                results.append({
                    "Test Case": f"Answer Paper {i+1} Link Verification",
                    "Status": f"Fail: {str(e)}",
                    "Expected URL": expected_answers_urls[i],
                    "Actual URL": self.driver.current_url if self.driver.current_url else "N/A",
                    "Screenshot": screenshot_path
                })

                # Ensure the tab is closed and return to the main tab
                if len(self.driver.window_handles) > 1:
                    self.driver.close()
                    self.driver.switch_to.window(self.driver.window_handles[0])

            # Go back to the main page for the next link
            self.driver.get(main_page_url)
            time.sleep(3)

        # Log results to CSV
        self.append_to_csv(results)

        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        print(f"Total test duration: {round(duration, 2)} seconds")