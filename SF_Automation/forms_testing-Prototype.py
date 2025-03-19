#!/usr/bin/env python3
"""
modal_form_tester.py - Comprehensive form testing suite for Software Finder
Tests all forms including single-step and multi-step forms
"""
import logging
import json
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('form_testing.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Form configurations
form_configs = [
    # Get Recommendation CTA Form (Single-step)
    {
        "form_type": "Get Recommendation CTA Form",
        "page_url": "https://www.softwarefinder.com/",
        "access_method": "direct",
        "form_locator": "#Get\\ Recommendation\\ CTA\\ Form",
        "submit_button": {
            "by": By.CSS_SELECTOR,
            "value": "button[type='submit']"
        },
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "tel",
                "selectors": ["[name='phone']", "#phone"]
            },
            "email": {
                "value": "test@example.com",
                "type": "email",
                "selectors": ["[name='email']", "#email"]
            },
            "organization": {
                "value": "Test Org",
                "type": "text",
                "selectors": [
                    "[name='company']",
                    "#company",
                    "[name='organization']",
                    "#organization"
                ]
            }
        }
    },
    # Get Pricing CTA Form (Single-step)
    {
        "form_type": "Get Pricing CTA Form",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "button.text-white.bg-black"),
        "form_locator": "#Get\\ Pricing\\ CTA\\ Form",
        "submit_button": {
            "by": By.CSS_SELECTOR,
            "value": "button[type='submit']"
        },
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "tel",
                "selectors": ["[name='phone']", "#phone"]
            },
            "email": {
                "value": "test@example.com",
                "type": "email",
                "selectors": ["[name='email']", "#email"]
            },
            "organization": {
                "value": "Test Org",
                "type": "text",
                "selectors": [
                    "[name='company']",
                    "#company",
                    "[name='organization']",
                    "#organization"
                ]
            }
        }
    },
    # Write a Review Form (Multi-step)
    {
        "form_type": "Write a Review Form",
        "page_url": "https://softwarefinder.com/software-development/techlogix",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "button[data-testid='write-review-button']"),
        "form_locator": "form.review-form",
        "submit_button": {
            "by": By.CSS_SELECTOR,
            "value": "button[type='submit']"
        },
        "is_multi_step": True,
        "steps": [
            # Step 1: Personal Information
            {
                "fields": {
                    "author": {
                        "value": "Test User",
                        "type": "text",
                        "selectors": ["[name='author']", "#author"]
                    },
                    "organization": {
                        "value": "Test Org",
                        "type": "text",
                        "selectors": ["[name='organization']", "#organization"]
                    },
                    "Industry": {
                        "value": "Analytics",
                        "type": "select",
                        "selectors": ["select[name='Industry']", "#Industry"]
                    },
                    "time_used": {
                        "value": "Free Trial",
                        "type": "select",
                        "selectors": ["select[name='time_used']", "#time_used"]
                    },
                    "team_size": {
                        "value": "101-500",
                        "type": "select",
                        "selectors": ["select[name='team_size']", "#team_size"]
                    }
                },
                "next_button": {
                    "by": By.CSS_SELECTOR,
                    "value": "button[type='button'][data-next]"
                },
                "wait_for": "[name='title']"
            },
            # Step 2: Review Details
            {
                "fields": {
                    "title": {
                        "value": "Test Review",
                        "type": "text",
                        "selectors": ["[name='title']", "#title"]
                    },
                    "pros_text": {
                        "value": "Great functionality",
                        "type": "textarea",
                        "selectors": ["[name='pros_text']", "#pros_text"]
                    },
                    "cons_text": {
                        "value": "Needs more features",
                        "type": "textarea",
                        "selectors": ["[name='cons_text']", "#cons_text"]
                    }
                },
                "next_button": {
                    "by": By.CSS_SELECTOR,
                    "value": "button[type='button'][data-next]"
                },
                "wait_for": "div.rating-section"
            },
            # Step 3: Ratings
            {
                "ratings": [
                    {"label": "Ease of use", "value": 7},
                    {"label": "Value for money", "value": 8},
                    {"label": "Customer Support", "value": 6},
                    {"label": "Functionality", "value": 9}
                ],
                "overall_rating": {
                    "value": 4,
                    "type": "star",
                    "selector": "div.overall-rating"
                }
            }
        ]
    }
]

class FormTester:
    def __init__(self, headless=True):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 30)  # Extended timeout
        self.actions = ActionChains(self.driver)
        logger.info("Chrome WebDriver initialized successfully")
        self.results = []

    def find_element_by_selectors(self, parent, selectors):
        """Try multiple selectors to find an element"""
        for selector in selectors:
            try:
                element = parent.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    logger.info(f"Found element using selector: {selector}")
                    return element
            except:
                continue
        return None

    def find_button(self, config):
        """Find and return the form button"""
        self.driver.get(config["page_url"])
        time.sleep(2)
        logger.info(f"Current URL: {self.driver.current_url}")

        # Try configured locator first
        if config.get("button_locator"):
            try:
                button = self.wait.until(EC.element_to_be_clickable(config["button_locator"]))
                logger.info("Found button with configured locator")
                return button
            except:
                pass

        # Try finding by text
        buttons = self.driver.find_elements(By.TAG_NAME, "button")
        logger.info(f"Found {len(buttons)} buttons on page")

        for button in buttons:
            try:
                text = button.text.lower()
                if any(keyword in text for keyword in ["recommend", "get free", "pricing", "write review"]):
                    if button.is_displayed() and button.is_enabled():
                        logger.info(f"Found button with text: {text}")
                        return button
            except:
                continue

        raise Exception(f"Could not find button for {config['form_type']}")

    def find_form(self, config):
        """Find and return the form"""
        time.sleep(2)  # Wait for modal animation

        try:
            form = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, config["form_locator"]))
            )
            logger.info(f"Found form with ID: {form.get_attribute('id')}")
            return form
        except:
            raise Exception(f"Could not find form for {config['form_type']}")

    def fill_select_field(self, form, field_name, field_config):
        """Fill a select dropdown field"""
        field = self.find_element_by_selectors(form, field_config["selectors"])
        if not field:
            raise Exception(f"Could not find select field: {field_name}")

        select = Select(field)
        select.select_by_visible_text(field_config["value"])
        logger.info(f"Selected {field_config['value']} for {field_name}")

    def set_rating(self, form, rating_config):
        """Set star rating value"""
        try:
            rating_container = form.find_element(By.CSS_SELECTOR, rating_config["selector"])
            stars = rating_container.find_elements(By.CSS_SELECTOR, "span[data-rating]")

            for star in stars:
                if int(star.get_attribute("data-rating")) == rating_config["value"]:
                    star.click()
                    logger.info(f"Set rating to {rating_config['value']}")
                    return

            raise Exception(f"Could not find star rating option: {rating_config['value']}")
        except Exception as e:
            raise Exception(f"Error setting rating: {str(e)}")

    def handle_multi_step_form(self, form, config):
        """Handle multi-step form submission"""
        try:
            for step_index, step in enumerate(config["steps"]):
                logger.info(f"Handling step {step_index + 1}")

                # Fill fields for this step
                if "fields" in step:
                    for field_name, field_config in step["fields"].items():
                        if field_config["type"] == "select":
                            self.fill_select_field(form, field_name, field_config)
                        else:
                            field = self.find_element_by_selectors(form, field_config["selectors"])
                            if not field:
                                raise Exception(f"Could not find field: {field_name}")

                            field.clear()
                            field.send_keys(field_config["value"])
                            logger.info(f"Filled {field_name} with {field_config['value']}")

                # Handle ratings if present
                if "ratings" in step:
                    for rating in step["ratings"]:
                        slider = form.find_element(By.XPATH, f"//label[contains(text(), '{rating['label']}')]/..//input[type='range']")
                        self.actions.drag_and_drop_by_offset(
                            slider,
                            int(rating["value"] * slider.size["width"] / 10),
                            0
                        ).perform()
                        logger.info(f"Set {rating['label']} rating to {rating['value']}")

                # Handle overall rating if present
                if "overall_rating" in step:
                    self.set_rating(form, step["overall_rating"])

                # Move to next step if not the last one
                if step_index < len(config["steps"]) - 1:
                    next_button = form.find_element(
                        step["next_button"]["by"],
                        step["next_button"]["value"]
                    )
                    next_button.click()
                    logger.info("Clicked next button")

                    # Wait for next step
                    if "wait_for" in step:
                        self.wait.until(
                            EC.presence_of_element_located((By.CSS_SELECTOR, step["wait_for"]))
                        )
                        time.sleep(1)  # Brief pause for animations

            # Submit the final step
            submit_button = form.find_element(
                config["submit_button"]["by"],
                config["submit_button"]["value"]
            )
            submit_button.click()
            logger.info("Clicked submit button")

        except Exception as e:
            raise Exception(f"Error in multi-step form: {str(e)}")

    def verify_fields(self, form, fields):
        """Verify form fields are present and of correct type"""
        field_elements = {}

        for field_name, field_config in fields.items():
            try:
                field = self.find_element_by_selectors(form, field_config["selectors"])
                if not field:
                    raise Exception(f"Could not find field with any selector")

                actual_type = field.get_attribute("type")
                expected_type = field_config["type"]
                if actual_type != expected_type:
                    logger.warning(f"Field type mismatch: expected {expected_type}, got {actual_type}")

                field_elements[field_name] = field
                logger.info(f"Verified field: {field_name}")

            except Exception as e:
                raise Exception(f"Field verification failed for {field_name}: {str(e)}")

        return field_elements

    def check_success_indicators(self):
        """Check for various success indicators after form submission"""
        try:
            # Check URL for success patterns
            current_url = self.driver.current_url
            if "thank-you" in current_url or "success" in current_url:
                logger.info(f"Success: URL contains success indicator")
                return True

            # Check for success messages
            success_selectors = [
                ".success-message",
                ".thank-you-page",
                "[data-testid='success-message']",
                ".form-success",
                "#success-message",
                "div[role='alert']"
            ]

            for selector in success_selectors:
                try:
                    element = self.driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        text = element.text.lower()
                        if any(word in text for word in ["success", "thank", "submitted", "received"]):
                            logger.info(f"Success: Found message - {text}")
                            return True
                except:
                    continue

            # Check for success text in page
            page_text = self.driver.page_source.lower()
            success_phrases = [
                "thank you",
                "submitted successfully",
                "we'll be in touch",
                "submission received",
                "review submitted"
            ]
            if any(phrase in page_text for phrase in success_phrases):
                logger.info("Success: Found success text in page")
                return True

            return False

        except Exception as e:
            logger.error(f"Error checking success indicators: {str(e)}")
            return False

    def test_form(self, config):
        """Run all tests for a form"""
        result = {
            "form_type": config["form_type"],
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }

        try:
            # SF-26: Button visibility
            button = self.find_button(config)
            result["tests"].append({
                "id": "SF-26",
                "description": "Button visibility",
                "status": "Passed"
            })
            logger.info("SF-26: PASSED ✅")

            # SF-27: Form opens
            button.click()
            form = self.find_form(config)
            result["tests"].append({
                "id": "SF-27",
                "description": "Form opens",
                "status": "Passed"
            })
            logger.info("SF-27: PASSED ✅")

            # Handle form based on type
            if config.get("is_multi_step", False):
                # Multi-step form
                self.handle_multi_step_form(form, config)
            else:
                # Single-step form
                # SF-28-31: Field verification
                field_elements = self.verify_fields(form, config["fields"])
                result["tests"].append({
                    "id": "SF-28-31",
                    "description": "Field verification",
                    "status": "Passed"
                })
                logger.info("SF-28-31: PASSED ✅")

                # Fill and submit form
                for field_name, field_config in config["fields"].items():
                    field = field_elements[field_name]
                    field.clear()
                    field.send_keys(field_config["value"])
                    logger.info(f"Filled {field_name} with {field_config['value']}")

                submit_button = form.find_element(
                    config["submit_button"]["by"],
                    config["submit_button"]["value"]
                )
                submit_button.click()
                logger.info("Clicked submit button")

            # SF-34: Verify submission
            success = False
            attempts = 0
            max_attempts = 3

            while not success and attempts < max_attempts:
                attempts += 1
                logger.info(f"Checking submission status (attempt {attempts}/{max_attempts})")

                time.sleep(5)

                try:
                    # Check if form is still visible
                    try:
                        if not form.is_displayed():
                            logger.info("Success: Form is no longer visible")
                            success = True
                            break
                    except StaleElementReferenceException:
                        logger.info("Success: Form element is stale (removed from DOM)")
                        success = True
                        break
                    except:
                        pass

                    # Check other success indicators
                    if self.check_success_indicators():
                        success = True
                        break

                except Exception as e:
                    logger.warning(f"Check attempt failed: {str(e)}")
                    if attempts == max_attempts:
                        raise

            if success:
                result["tests"].append({
                    "id": "SF-34",
                    "description": "Form submission",
                    "status": "Passed"
                })
                logger.info("SF-34: PASSED ✅")
                result["status"] = "Passed"
                print(f"\n{config['form_type']}: All tests passed! ✅")
            else:
                raise Exception("Could not verify successful form submission")

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error testing {config['form_type']}: {error_msg}")
            result["status"] = "Failed"
            result["error"] = error_msg
            print(f"\n{config['form_type']}: Tests failed ❌")
            print(f"Error: {error_msg}")

        self.results.append(result)
        return result

    def run_tests(self):
        """Run tests for all forms"""
        try:
            print("\nStarting form testing...")
            for config in form_configs:
                self.test_form(config)
            print("\nAll form tests completed!")
            return True
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            return False
        finally:
            self.driver.quit()

    def generate_report(self):
        """Generate executive report"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r["status"] == "Passed")
        failed = total - passed

        report = {
            "summary": {
                "total_forms": total,
                "passed_forms": passed,
                "failed_forms": failed,
                "success_rate": f"{(passed/total*100) if total > 0 else 0:.1f}%"
            },
            "details": self.results,
            "timestamp": datetime.now().isoformat()
        }

        filename = f'form_testing_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2)

        return filename

def print_summary(report_file):
    """Print test summary"""
    with open(report_file) as f:
        report = json.load(f)

    print("\n========== TEST SUMMARY ==========")
    print(f"Total Forms Tested: {report['summary']['total_forms']}")
    print(f"Forms Passed: {report['summary']['passed_forms']}")
    print(f"Forms Failed: {report['summary']['failed_forms']}")
    print(f"Success Rate: {report['summary']['success_rate']}")

    print("\nDetailed Results:")
    for form in report["details"]:
        print(f"\nForm: {form['form_type']}")
        print(f"Status: {form['status']}")
        if form.get("error"):
            print(f"Error: {form['error']}")
        print("\nTest Cases:")
        for test in form["tests"]:
            print(f"  {test['id']}: {test['status']} - {test['description']}")

    print("\n================================")

def main():
    tester = FormTester(headless=True)
    try:
        tester.run_tests()
        report_file = tester.generate_report()
        print_summary(report_file)
    except Exception as e:
        logger.error(f"Test execution failed: {str(e)}")
        raise

if __name__ == "__main__":
    main()