import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

form_configs = [
    # Homepage: Get Recommendation CTA Form (Single-step)
    {
        "form_type": "Get Recommendation CTA Form",
        "page_url": "https://www.softwarefinder.com/",
        "access_method": "direct",  
        "form_locator": (By.ID, "Get Recommendation CTA Form"),  
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\\ Recommendation\\ CTA\\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },

    # Vendor Profile: Get Pricing CTA Form (Single-step)
    {
        "form_type": "Get Pricing CTA Form",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\\:justify-start.md\\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-black.hover\\:bg-dark-blue.text-sm.py-2.px-2.md\\:px-7"),
        "form_locator": (By.ID, "radix-:r2q:"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\\ Pricing\\ CTA\\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=pricing"}
    },

    # Vendor Profile: Watch Demo CTA Form (Single-step)
    {
        "form_type": "Watch Demo CTA Form",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-green.hover\:bg-dark-green.text-sm.py-2.px-2.md\:px-7"), 
        "form_locator": (By.ID, "radix-:r3f:"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Watch\ Demo\ CTA\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=demo"}
    },

    # Vendor Profile (Service): Get Quote CTA Form (Single-step)
    {
        "form_type": "Get Quote CTA Form",
        "page_url": "https://softwarefinder.com/software-development/rolustech",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-green.hover\:bg-dark-green.text-sm.py-2.px-2.md\:px-7"),
        "form_locator": (By.ID, "Get a Quote CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "message": "Test Message 123"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\ a\ Quote\ CTA\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=quote"}
    },

    # Vendor Profile (Service): Download Portfolio CTA Form (Single-step)
    {
        "form_type": "Download Portfolio CTA Form",
        "page_url": "https://softwarefinder.com/software-development/rolustech",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-black.hover\:bg-dark-blue.text-sm.py-2.px-2.md\:px-7"), 
        "form_locator": (By.ID, "Download Portfolio CTA Form"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Download\ Portfolio\ CTA\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=portfolio"}
    },

    # Vendor Profile: Not Sure If Vendor Is the Right Fit? (Single-step)
    {
        "form_type": "Not sure if Vendor is the right fit?",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "direct",
        "form_locator": (By.ID, "Not sure if Vendor is the right fit?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Not\\ sure\\ if\\ Vendor\\ is\\ the\\ right\\ fit\\? > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },

    # Vendor Profile: Write a Review (Multi-step)
    {
        "form_type": "Write a Review",
        "page_url": "https://softwarefinder.com/software-development/techlogix",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > section:nth-child(6) > div > section.ugc-content > div.hidden.mt-12.mb-8.xl\\:block > div > div.flex.flex-col.items-center.justify-center.gap-8 > button"),
        "form_locator": (By.CLASS_NAME, "ReviewForm_right__2i_8N"),
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
                "pros_text": "Great functionality",
                "cons_text": "Needs more features",
                "next": True,
                "wait_for": (By.XPATH, "//p[text()='Ease of use']")
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
        "submit_button": (By.XPATH, "//button[@type='submit']"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=review"}
    },

    # For Vendor: Get Started, Lead Generation(Single-step)
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
            "message": "test Message"
        },
        "submit_button": (By.CSS_SELECTOR, "#Get\ Started\ \(For\ Vendors\) > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },

    # Price Guide: Price Guide Sub-Category Page(Single-step)
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

    # Price Guide: Product List Sub-Category Page(Single-step)
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

    # Resources: Side by Side Comparison (Single-step)
    {
        "form_type": "Side by Side Comparison",
        "page_url": "https://softwarefinder.com/resources/jazzhr-vs-breezy",
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

    # Resources: Download Whitepaper (Single-step)
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

    # Webinar: On demand, Registration (Single-step)
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
        "submit_button": (By.CSS_SELECTOR, "#On-Demand\ Software\ Review > button"),
        #"success_condition": {"type": "redirect", "url_contains": "resources/other-files"} # need to add a different success condition. The page refreshes and the form data is cleared
    },
    
    # Webinar: On demand, Watch (Single-step)
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
        "submit_button": (By.CSS_SELECTOR, "#On-Demand\ Software\ Review > button"),
        #"success_condition":same as webinar registration
    },

    # Feeling overwhelmed by all the [Category Name] options listed? (Get Free Advice ) (Single-step)
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
        "submit_button": (By.CSS_SELECTOR, "#Feeling\ overwhelmed\ by\ all\ the\ Category\ option\ listed > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
    
    # Not Sure If [Add Page Title] Is the Right Fit? (Single-step)
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
        "submit_button": (By.CSS_SELECTOR, "#Not\ sure\ if\ Vendor\ is\ the\ right\ fit\? > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },

    # Need Help Finding [Category Name] Get Free Advice  (Single-step)
    {
        "form_type": "Need Help Finding",
        "page_url": "https://softwarefinder.com/emr-software",
        "access_method": "direct",
        "form_locator": (By.ID, "Need Help Finding Category Software"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Need\ Help\ Finding\ Category\ Software > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },
        
    # Need help Deciding? (Single-step)
    {
        "form_type": "Webinar on Demand Watch",
        "page_url": "https://softwarefinder.com/",
        "access_method": "direct",
        "form_locator": (By.ID, "Need help deciding ?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Need\ help\ deciding\ \? > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },    
    
    # Looking for Software? (Single-step)
    {
        "form_type": "Webinar on Demand Watch",
        "page_url": "https://softwarefinder.com/",
        "access_method": "direct",
        "form_locator": (By.ID, "Looking for Software?"),
        "fields": {
            "name": "Test User",
            "phone": "1234567890",
            "email": "test@example.com",
            "organization": "Test Org"
        },
        "submit_button": (By.CSS_SELECTOR, "#Looking\ for\ Software\? > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    },   

    # Message us
    {
        'form_type': 'Feeling Overwhelmed By all',
        'page_url': 'https://softwarefinder.com/contact-us',
        'access_method': 'direct',
        'form_locator': (By.ID, 'Message Us'),
        'fields': {
            'name': 'Test User',
            'phone': '1234567890',
            'email': 'test@example.com',
            'organization': 'Test Org',
            "message": "Test Message 123"
        },
        "submit_button": (By.CSS_SELECTOR, "#Message\ Us > div > div.flex.items-center.justify-start.lg\:justify-end.w-full > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"}
    }
    
]

@pytest.fixture(scope="module")
def driver():
    """Set up and tear down the WebDriver."""
    driver = webdriver.Chrome()
    yield driver
    driver.quit()

@pytest.mark.parametrize('form_config', form_configs)
def test_form_submission(driver, form_config):
    """Test form filling and submission for each form configuration."""
    driver.get(form_config['page_url'])
    
    # Access the form if hidden behind a button
    if form_config['access_method'] == 'button':
        button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(form_config['button_locator'])
        )
        button.click()
    
    # Locate the form
    form = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(form_config['form_locator'])
    )
    
    # Handle fields (single-step or multi-step)
    fields = form_config['fields']
    if isinstance(fields, list):  # Multi-step form
        for step in fields:
            for field, value in step.items():
                if field == 'next':
                    continue
                if isinstance(value, dict) and 'type' in value:
                    if value['type'] == 'select':
                        select = Select(form.find_element(By.NAME, field))
                        select.select_by_visible_text(value['value'])
                    elif value['type'] == 'star':
                        star = form.find_element(By.XPATH, f'//span[@data-rating="{value["value"]}"]')  # Adjust locator
                        star.click()
                else:
                    input_field = form.find_element(By.NAME, field)
                    input_field.clear()
                    input_field.send_keys(value)
            if step.get('next', False):
                next_button = form.find_element(By.XPATH, '//button[contains(text(), "Next")]')  # Adjust locator
                next_button.click()
    else:  # Single-step form
        for field, value in fields.items():
            input_field = form.find_element(By.NAME, field)
            input_field.clear()
            input_field.send_keys(value)
    
    # Submit the form
    submit_button = form.find_element(By.XPATH, '//button[@type="submit"]')  # Adjust locator
    submit_button.click()
    
    # Verify successful submission
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, 'success-message'))  # Adjust locator
    )