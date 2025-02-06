'''runs using 
pytest automatedTests.py -v --html=report.html --self-contained-html --reruns 2 --reruns-delay 5

# can be used for notification service in case of an error
chrome_options.add_experimental_option(
    "prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.geolocation": 2,
    }
)
'''
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import csv
from datetime import datetime
import os
import time

@pytest.fixture(scope="module")
def driver():
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--headless")
    # Force desktop layout settings:
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--force-device-scale-factor=1")
    chrome_options.add_argument("--disable-gpu")
    # Set a desktop user-agent:
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "prefs", {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_setting_values.geolocation": 2,
        }
    )
    
    # Initialize WebDriver
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.implicitly_wait(5)  # Fallback implicit wait
    yield driver
    
    # Teardown
    try:
        driver.quit()
    except Exception as e:
        print(f"Error during teardown: {str(e)}")

def save_results(test_case, status, error_message=""):
    file_path = os.path.abspath("test_results.csv")
    try:
        with open(file_path, "a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([test_case, status, error_message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    except PermissionError:
        print(f"Permission denied for file: {file_path}")
        raise

def ensure_interactable(element, driver):
    """Advanced element readiness check"""
    try:
        # Scroll into view
        driver.execute_script("arguments[0].scrollIntoViewIfNeeded();", element)
        
       # Wait for element stability
        WebDriverWait(driver, 15).until(
            lambda d: element.is_displayed() and element.is_enabled() and element.rect['width'] > 0 and element.rect['height'] > 0
        )
        
        # Optionally, move to the element
        action = webdriver.ActionChains(driver)
        action.move_to_element(element).pause(0.3).perform()
        
        
        return element
    except Exception as e:
        driver.save_screenshot("element_interaction_error.png")
        raise

def wait_for_page_load(driver, timeout=30):
    WebDriverWait(driver, timeout).until(
        lambda d: d.execute_script("return document.readyState") == "complete"
    )
    time.sleep(1)  # Allow for JavaScript initializations

def safe_click(element, driver):
    """JavaScript click alternative"""
    try:
        element.click()
    except:
        # Scroll the element into view again just in case
        driver.execute_script("arguments[0].scrollIntoView(true);", element)
        # Perform a JS click as a fallback
        driver.execute_script("arguments[0].click();", element)

def safe_send_keys(element, text, driver, clear_first=True):
    """Robust text input with error handling"""
    try:
        # Ensure element is ready
        WebDriverWait(driver, 10).until(
            lambda d: element.is_displayed() 
            and element.is_enabled()
            and element.get_attribute("readonly") is None
        )
        
        # Alternative clearing method
        if clear_first:
            current_value = element.get_attribute("value")
            if current_value:
                element.click()
                element.send_keys(Keys.CONTROL + "a")
                element.send_keys(Keys.DELETE)
                WebDriverWait(driver, 3).until(
                    lambda d: element.get_attribute("value") == ""
                )
        
        # Type text with verification
        for char in text:
            element.click()
            element.send_keys(char)
            time.sleep(0.05)
            
        # Verify final text
        WebDriverWait(driver, 3).until(
            lambda d: element.get_attribute("value") == text
        )
        
    except Exception as e:
        driver.execute_script(f"arguments[0].value = '{text}';", element)
        element.click()
        element.send_keys(" " + Keys.BACKSPACE)
        raise e

# Test Case 1: Valid keyword search
def test_search_accuracy(driver):
    try:
        driver.get("https://www.softwarefinder.com")
        
        # Wait for page readiness
        wait_for_page_load(driver)
        
        # Dismiss potential overlays
        driver.execute_script("window.focus();")
        
        # Locate and interact with search box
        search_box = WebDriverWait(driver, 25).until(
            EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Search Software, Category, Service..']"))

        )

        driver.get_screenshot_as_file("headless_debug.png")
        with open("headless_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)

        search_box = ensure_interactable(search_box, driver)
        
        # Input text
        safe_send_keys(search_box, "data",driver)
        
        # Verify dropdown
        WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, ".SearchDropDown_body__191ZO"))
        )
        
        # Verify dropdown sections
        driver.find_element(By.XPATH, "//div[contains(text(),'Products')]")
        driver.find_element(By.XPATH, "//div[contains(text(),'Category')]")
        
        # Click view results
        view_results_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "RightArrowLink_small__mX_vf"))
        )
        safe_click(view_results_btn, driver)
        
        # Verify results page
        header = WebDriverWait(driver, 15).until(
            EC.visibility_of_element_located((By.CLASS_NAME, "PageHeaderTransparent_header__WP822"))
        )
        
        assert "data" in header.text.lower(), "Search term missing in header"
        assert "search result" in header.text.lower(), "Not on results page"
        
        results_container = driver.find_element(By.CLASS_NAME, "container")
        assert len(results_container.find_elements(By.XPATH, ".//*")) > 5, "Insufficient results"
        
        save_results("Search Accuracy", "Pass")
        
        
    except Exception as e:
        driver.save_screenshot("search_accuracy_error.png")
        save_results("Search Accuracy", "Fail", str(e))
        raise

# Test Case 2: Empty search
def test_empty_search(driver):
    try:
        driver.get("https://www.softwarefinder.com")
        
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search Software, Category, Service..']"))
        )
        search_box = ensure_interactable(search_box, driver)
        
        # Click and press enter
        search_box.click()
        safe_send_keys(search_box, " ",driver)
        
        # Wait for page stability
        wait_for_page_load(driver)
        
        assert "search-result" not in driver.current_url, "Empty search redirected"
        save_results("Empty Search", "Pass")
        
    except Exception as e:
        save_results("Empty Search", "Fail", str(e))
        raise

# Test Case 3: Special characters
def test_special_characters_search(driver):
    try:
        driver.get("https://www.softwarefinder.com")
        
        search_box = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@placeholder='Search Software, Category, Service..']"))
        )
        search_box = ensure_interactable(search_box, driver)
        
        # Type special characters
        search_box.click()
        safe_send_keys(search_box, "@#$%",driver, clear_first=False)
        time.sleep(0.1)
            
        # Verify no dropdown
        WebDriverWait(driver, 5).until(
            EC.invisibility_of_element_located((By.CLASS_NAME, "SearchDropDown_body__191ZO"))
        )
        
        assert "search-result" not in driver.current_url, "Invalid search redirected"
        save_results("Special Characters Search", "Pass")
        
    except Exception as e:
        save_results("Special Characters Search", "Fail", str(e))
        raise

# Test Case 4: Filtering By Category
def test_filter_by_category(driver):
    try:
        driver.get("https://softwarefinder.com/project-management-software/all")
        
        industry_filter = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//p[text()='Industry']/following-sibling::div//label[text()='Analytics']"))
        )
        checkbox = industry_filter.find_element(By.XPATH, "./preceding-sibling::button")
        checkbox.click()
        
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, ".CategoryListItem_box__pzjBg:not([style*='display: none'])"))
        )
        
        results = driver.find_elements(By.CLASS_NAME, "CategoryListItem_box__pzjBg")
        assert len(results) > 0, "No filtered results found"
        save_results("Filter by Category", "Pass")
        
    except Exception as e:
        save_results("Filter by Category", "Fail", str(e))
        raise

# Test Case 5: Filtering By Rating
def test_filter_by_rating(driver):
    try:
        # Navigate to the page with the filter options.
        driver.get("https://softwarefinder.com/lms/360learning/reviews")
        wait_for_page_load(driver)
        
        # Wait until the filter section is loaded.
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CLASS_NAME, "Filters_filter__ZR3gT"))
        )
        
        # Locate the 5-star rating checkbox by its id attribute.
        five_star_checkbox = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@role='checkbox' and @id='5']"))
        )
        five_star_checkbox.click()
        
        # Wait until the filtered results are visible.
        WebDriverWait(driver, 15).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "VendorReviewMiniItem_box__hseS6"))
        )
        
        # Retrieve the filtered results.
        results = driver.find_elements(By.CLASS_NAME, "VendorReviewMiniItem_box__hseS6")
        assert len(results) > 0, "No results found after applying the rating filter"
        
        # Save a "Pass" result in the CSV.
        save_results("Filter by Rating", "Pass")
    
    except Exception as e:
        # Save a "Fail" result along with the error message in the CSV.
        save_results("Filter by Rating", "Fail", str(e))
        raise
    
if __name__ == "__main__":
    pytest.main(["-v", "-s", "--html=report.html", "--self-contained-html", "--reruns=2", "--reruns-delay=5"])