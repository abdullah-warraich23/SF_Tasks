import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import uuid
import time

# Form configurations with updated success conditions for webinar forms
form_configs = [
    # 1. Homepage: Get Recommendation (CTA Form)
    {
        "form_type": "Get Recommendation CTA Form",
        "page_url": "https://www.softwarefinder.com/",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/div/div/div/div[1]/div[2]/button"),
        "form_locator": (By.ID, "Get Recommendation CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\ Recommendation\ CTA\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 2. Vendor Profile: Get Pricing CTA Form (CTA Form)
    {
        "form_type": "Get Pricing CTA Form",
        "page_url": "https://softwarefinder.com/crm/hubspot",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-black.hover\:bg-dark-blue.text-sm.py-2.px-2.md\:px-7"),
        "form_locator": (By.ID, "Get Pricing CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[2]"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=pricing"}
    },
    # 3. Vendor Profile: Watch Demo CTA Form (CTA Form)
    {
        "form_type": "Watch Demo CTA Form",
        "page_url": "https://softwarefinder.com/artificial-intelligence/v7-software",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-green.hover\:bg-dark-green.text-sm.py-2.px-2.md\:px-7"),
        "form_locator": (By.ID, "Watch Demo CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Watch\\ Demo\\ CTA\\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=demo"}
    },
    # 4. Vendor Profile (Service): Get Quote CTA Form (CTA Form)
    {
        "form_type": "Get Quote CTA Form",
        "page_url": "https://softwarefinder.com/software-development/techlogix",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[1]"),
        "form_locator": (By.ID, "Get a Quote CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "Message": "Test Message 123"
        },
        "submit_button": (By.XPATH, "//*[@id='Get a Quote CTA Form']/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=quote"}
    },
    # 5. Vendor Profile (Service): Download Portfolio (CTA Form)
    {
        "form_type": "Download Portfolio CTA Form",
        "page_url": "https://softwarefinder.com/software-development/rolustech",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[2]"),
        "form_locator": (By.ID, "Download Portfolio CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Download Portfolio CTA Form']/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=portfolio"}
    },
    # 6. Vendor Profile: Not Sure If Vendor Is the Right Fit? (Single-step)
    {
        "form_type": "Not Sure if Vendor is the Right Fit?",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "direct",
        "form_locator": (By.ID, "Not sure if Vendor is the right fit?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Not sure if Vendor is the right fit?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 7. Vendor Profile: Write a Review (Multi-step)
    {
        "form_type": "Write a Review",
        "page_url": "https://softwarefinder.com/software-development/techlogix",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/div[2]/section[2]/div/div/div[1]/button"),
        "form_locator": (By.ID, "reviews"),
        "fields": [
            # Step 1: Personal Information
            {
                "author": "Test User",
                "organization": "Test Org",
                "Industry": {"type": "select", "value": "Analytics"},
                "time_used": {"type": "select", "value": "Free Trial"},
                "team_size": {"type": "select", "value": "101-500"},
                "next": True,
                "wait_for": (By.NAME, "title")
            },
            # Step 2: Review Details
            {
                "title": "Test Review",
                "pros_text": "TEST PRO",
                "cons_text": "TEST CON",
                "next": True,
                "wait_for": (By.XPATH, "//*[@id='reviews']/div/div[2]/div[2]/div[1]")
            },
            # Step 3: Ratings
            {
                "sliders": [
                    {"label": "Ease of use", "value": 7},
                    {"label": "Value for money", "value": 8},
                    {"label": "Customer Support", "value": 6},
                    {"label": "Functionality", "value": 9}
                ],
                "rating": 4,  # 4-star rating
                "next": False
            }
        ],
        "submit_button": (By.XPATH, "//*[@id='reviews']/div/div[2]/div[2]/div[2]/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=review"}
    },
    # 8. For Vendor: Get Started, Lead Generation (Single-step)
    {
        "form_type": "Get Started Form",
        "page_url": "https://softwarefinder.com/lead-generation-services",
        "access_method": "direct",
        "form_locator": (By.ID, "Get Started (For Vendors)"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org",
            "Message": "Test Message"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\ Started\ \(For\ Vendors\) > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 9. Price Guide: Price Guide Sub-Category Page (Single-step)
    {
        "form_type": "Price Guide Sub-category",
        "page_url": "https://softwarefinder.com/construction/ai-construction-software",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "#pricing-guide > section > div > div > div.flex.items-center.justify-start.w-full.lg\:col-span-2.lg\:justify-end > button"),
        "form_locator": (By.ID, "Get Pricing Guide"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\ Pricing\ Guide > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"}
    },
    # 10. Price Guide: Product List Sub-Category Page (Single-step)
    {
        "form_type": "Product List Sub-category",
        "page_url": "https://softwarefinder.com/construction/ai-construction-software",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > div.relative.-mt-14 > div > div > button"),
        "form_locator": (By.ID, "Download Sub category List"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Download\ Sub\ category\ List > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"}
    },
    # 11. Resources: Side by Side Comparison (Single-step)
    {
        "form_type": "Side by Side Comparison",
        "page_url": "https://softwarefinder.com/resources/blackboard-vs-canvas-comparison",
        "access_method": "direct",
        "form_locator": (By.ID, "Side-by-Side Review"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Side-by-Side\ Review > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 12. Resources: Download Whitepaper (Single-step)
    {
        "form_type": "Download Whitepaper",
        "page_url": "https://softwarefinder.com/resources/5-top-rated-payroll-software-for-small-businesses",
        "access_method": "direct",
        "form_locator": (By.ID, "Download Whitepaper"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Download\ Whitepaper > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"}
    },
    # 13. Webinar: On Demand, Registration (Single-step)
    {
        "form_type": "Webinar on Demand Registration",
        "page_url": "https://softwarefinder.com/resources/building-a-resilient-workforce-ai-driven-hr-tools-for-recruitment-and-performance-tracking",
        "access_method": "direct",
        "form_locator": (By.ID, "On-Demand Software Review"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='On-Demand Software Review']/button"),
        "success_condition": {"type": "form_cleared"}
    },
    # 14. Webinar: On Demand, Watch (Single-step)
    {
        "form_type": "Webinar on Demand Watch",
        "page_url": "https://softwarefinder.com/resources/ol-2-regulatory-compliance-new-medical-practices",
        "access_method": "direct",
        "form_locator": (By.ID, "On-Demand Software Review"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='On-Demand Software Review']/button"),
        "success_condition": {"type": "form_cleared"}
    },
    # 15. Feeling Overwhelmed By Options Listed (Single-step)
    {
        "form_type": "Feeling Overwhelmed By Options Listed",
        "page_url": "https://softwarefinder.com/retail",
        "access_method": "direct",
        "form_locator": (By.ID, "Feeling overwhelmed by all the Category option listed"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Feeling overwhelmed by all the Category option listed']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 16. Not Sure If Right Fit (Single-step)
    {
        "form_type": "Not Sure if Right Fit",
        "page_url": "https://softwarefinder.com/emr-software/athenahealth",
        "access_method": "direct",
        "form_locator": (By.ID, "Not sure if Vendor is the right fit?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Not sure if Vendor is the right fit?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 17. Need Help Finding (Single-step)
    {
        "form_type": "Need Help Finding",
        "page_url": "https://softwarefinder.com/emr-software",
        "access_method": "direct",
        "form_locator": (By.ID,"Need Help Finding Category Software"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Need Help Finding Category Software']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 18. Need Help Deciding? (Single-step)
    {
        "form_type": "Need Help Deciding?",
        "page_url": "https://softwarefinder.com/",
        "access_method": "direct",
        "form_locator": (By.ID, "Need help deciding ?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Need help deciding ?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 19. Looking for Software? (Single-step)
    {
        "form_type": "Looking for Software?",
        "page_url": "https://softwarefinder.com/resources",
        "access_method": "direct",
        "form_locator": (By.ID, "Looking for Software?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.XPATH, "//*[@id='Looking for Software?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    # 20. Message Us (Single-step)
    {
        "form_type": "Message Us",
        "page_url": "https://softwarefinder.com/contact-us",
        "access_method": "direct",
        "form_locator": (By.ID, "Message Us"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org",
            "Message": "Test Message 123"
        },
        "submit_button": (By.XPATH, "//*[@id='Message Us']/div/div[3]/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    }
]

# Helper Functions
def generate_unique_email():
    """Generate a unique email address for each test run."""
    return f"test_{uuid.uuid4().hex[:8]}@mail.com"

def scroll_into_view(driver, element):
    """Scroll the element into view."""
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    time.sleep(0.5)  # Brief pause to ensure scroll completes

def is_form_cleared(driver, form_locator):
    """Check if the form fields are cleared after submission."""
    try:
        form = driver.find_element(*form_locator)
        inputs = form.find_elements(By.TAG_NAME, "input")
        for input_field in inputs:
            if input_field.get_attribute("value"):
                return False
        return True
    except NoSuchElementException:
        return True  # Form not found, assume cleared

def check_success_condition(driver, success_condition, form_locator):
    """Check the success condition based on its type."""
    if success_condition["type"] == "redirect":
        try:
            WebDriverWait(driver, 10).until(
                EC.url_contains(success_condition["url_contains"])
            )
            return True
        except TimeoutException:
            return False
    elif success_condition["type"] == "form_cleared":
        time.sleep(2)  # Wait for potential refresh
        return is_form_cleared(driver, form_locator)
    return False

# Fixtures
@pytest.fixture(scope="module")
def driver():
    """Set up and tear down the WebDriver."""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

@pytest.fixture(scope="session")
def test_results():
    """Collect test results and generate a CSV report."""
    results = []
    yield results
    with open("test_report.csv", "w") as f:
        f.write("Form Type,Status,Message\n")
        for result in results:
            f.write(f"{result['form_type']},{result['status']},{result['Message']}\n")

# Test Function
@pytest.mark.parametrize("form_config", form_configs)
def test_form_submission(driver, form_config, test_results):
    """Test form filling and submission with scrolls and waits."""
    print(f"Testing form: {form_config['form_type']}")
    try:
        # Navigate to the page and wait for initial load
        driver.get(form_config["page_url"])
        time.sleep(2)  # Allow page to load fully

        # Access the form if hidden behind a button
        if form_config["access_method"] == "button":
            button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(form_config["button_locator"])
            )
            scroll_into_view(driver, button)
            WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(form_config["button_locator"])
            ).click()

        # Locate the form
        form = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(form_config["form_locator"])
        )
        scroll_into_view(driver, form)

        # Fill the fields
        for field, value in form_config["fields"].items():
            if field == "email":
                value = generate_unique_email()  # Unique email per test
            try:
                input_field = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.NAME, field))
                )
                scroll_into_view(driver, input_field)
                WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.NAME, field))
                )
                input_field.clear()
                input_field.send_keys(value)
            except TimeoutException:
                if field == "organization":
                    print(f"Warning: 'organization' field not found for {form_config['form_type']}, skipping...")
                    continue  # Skip optional fields like "organization"
                else:
                    raise Exception(f"Field '{field}' not found")

        # Submit the form
        submit_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(form_config["submit_button"])
        )
        scroll_into_view(driver, submit_button)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(form_config["submit_button"])
        ).click()

        # Check success condition
        success = check_success_condition(driver, form_config["success_condition"], form_config["form_locator"])
        if success:
            test_results.append({
                "form_type": form_config["form_type"],
                "status": "PASSED",
                "Message": "Form submitted successfully"
            })
            print(f"Form {form_config['form_type']} passed")
        else:
            test_results.append({
                "form_type": form_config["form_type"],
                "status": "FAILED",
                "Message": "Success condition not met"
            })
            pytest.fail("Success condition not met")

    except Exception as e:
        test_results.append({
            "form_type": form_config["form_type"],
            "status": "FAILED",
            "Message": str(e)
        })
        pytest.fail(str(e))

if __name__ == "__main__":
    pytest.main(["-v", __file__])