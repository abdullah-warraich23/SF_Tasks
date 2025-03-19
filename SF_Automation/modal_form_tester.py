#!/usr/bin/env python3
"""
modal_form_tester.py - Comprehensive form testing suite for Software Finder
Tests all forms including single-step and multi-step forms
"""
import logging
import json
import argparse
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (NoSuchElementException, 
                                        StaleElementReferenceException, 
                                        TimeoutException)
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

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
    # 1. Get Recommendation CTA Form (CTA Form)
    {
        "form_type": "Get Recommendation CTA Form",
        "page_url": "https://www.softwarefinder.com/",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/div/div/div/div[1]/div[2]/button"),
        "form_locator": (By.ID, "Get Recommendation CTA Form"),
        "submit_button": (By.CSS_SELECTOR, r"#Get\ Recommendation\ CTA\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 2. Get Pricing CTA Form (CTA Form)
    {
        "form_type": "Get Pricing CTA Form",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, r"body > main > section.VendorHeader_header__xWkrG > header > div > div.flex.flex-col.lg\:flex-row > div.VendorHeader_fixed_cta_header__PnoVY > button.w-full.text-center.justify-center.md\:justify-start.md\:w-auto.font-medium.rounded-full.flex.items-center.gap-3.transition-effect.text-white.bg-black.hover\:bg-dark-blue.text-sm.py-2.px-2.md\:px-7"),
        "form_locator": (By.ID, "Get Pricing CTA Form"),
        "submit_button": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[2]"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=pricing"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 3. Watch Demo CTA Form (CTA Form)
    {
        "form_type": "Watch Demo CTA Form",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "button.text-white.bg-green"),
        "form_locator": (By.ID, "Watch Demo CTA Form"),
        "submit_button": (By.CSS_SELECTOR, "#Watch\\ Demo\\ CTA\\ Form > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=demo"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 4. Get Quote CTA Form (CTA Form)
    {
        "form_type": "Get Quote CTA Form",
        "page_url": "https://softwarefinder.com/software-development/rolustech",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[1]"),
        "form_locator": (By.ID, "Get a Quote CTA Form"),
        "submit_button": (By.XPATH, "//*[@id='Get a Quote CTA Form']/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=quote"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
                "selectors": ["[name='phone']", "#phone"]
            },
            "email": {
                "value": "test@example.com",
                "type": "email",
                "selectors": ["[name='email']", "#email"]
            },
            "Message": {
                "value": "Test Message 123",
                "type": "textarea",
                "selectors": ["[name='Message']", "#Message"]
            }
        }
    },
    # 5. Download Portfolio CTA Form (CTA Form)
    {
        "form_type": "Download Portfolio CTA Form",
        "page_url": "https://softwarefinder.com/software-development/rolustech",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/section[1]/header/div/div[1]/div[3]/button[2]"),
        "form_locator": (By.ID, "Download Portfolio CTA Form"),
        "submit_button": (By.XPATH, "//*[@id='Download Portfolio CTA Form']/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=portfolio"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 6. Not Sure If Vendor Is the Right Fit? (Single-step)
    {
        "form_type": "Not Sure If Vendor Is the Right Fit?",
        "page_url": "https://softwarefinder.com/accounting-software/quickbooks",
        "access_method": "direct",
        "form_locator": (By.ID, "Not sure if Vendor is the right fit?"),
        "submit_button": (By.XPATH, "//*[@id='Not sure if Vendor is the right fit?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 7. Write a Review Form (Multi-step)
    {
        "form_type": "Write a Review Form",
        "page_url": "https://softwarefinder.com/software-development/techlogix",
        "access_method": "button",
        "button_locator": (By.XPATH, "/html/body/main/div[2]/section[2]/div/div/div[1]/button"),
        "form_locator": (By.CSS_SELECTOR, "#reviews > div > div.ReviewForm_FormResponsiveContainer__KRXea > div.ReviewForm_right__2i_8N > div.flex.flex-col.items-start.justify-center.mt-8"),
        "submit_button": (By.CSS_SELECTOR, "#reviews > div > div.ReviewForm_FormResponsiveContainer__KRXea > div.ReviewForm_right__2i_8N > div.flex.items-center.justify-between.mt-2 > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=review"},
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
                "next_button": (By.XPATH,"//*[@id='reviews']/div/div[2]/div[2]/div[2]/div[1]/button"),
                "wait_for": (By.CSS_SELECTOR, "[name='title']")
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
                        "value": "TEST PRO",
                        "type": "textarea",
                        "selectors": ["[name='pros_text']", "#pros_text"]
                    },
                    "cons_text": {
                        "value": "TEST CON",
                        "type": "textarea",
                        "selectors": ["[name='cons_text']", "#cons_text"]
                    }
                },
                "next_button": (By.XPATH, "//*[@id='reviews']/div/div[2]/div[2]/div[2]/div[1]/button"),
                "wait_for": (By.CSS_SELECTOR, "div.rating-section")
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
                    "selector": (By.XPATH, "//*[@id='reviews']/div/div[2]/div[2]/div[1]/div[5]//span[@class='star']")
                }
            }
        ]
    },
    # 8. Get Started Form (Single-step)
    {
        "form_type": "Get Started Form",
        "page_url": "https://softwarefinder.com/lead-generation-services",
        "access_method": "direct",
        "form_locator": (By.ID, "Get Started (For Vendors)"),
        "submit_button": (By.CSS_SELECTOR, r"#Get\ Started\ \(For\ Vendors\) > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
            },
            "Message": {
                "value": "Test Message",
                "type": "textarea",
                "selectors": ["[name='Message']", "#Message"]
            }
        }
    },
    # 9. Price Guide Sub-category Form (Single-step)
    {
        "form_type": "Price Guide Sub-category",
        "page_url": "https://softwarefinder.com/construction/ai-construction-software",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "#pricing-guide > section > div > div > div.flex.items-center.justify-start.w-full.lg\\:col-span-2.lg\\:justify-end > button"),
        "form_locator": (By.ID,"Get Pricing Guide"),
        "submit_button": (By.CSS_SELECTOR, r"#Get\ Pricing\ Guide > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 10. Product List Sub-category Form (Single-step)
    {
        "form_type": "Product List Sub-category",
        "page_url": "https://softwarefinder.com/construction/ai-construction-software",
        "access_method": "button",
        "button_locator": (By.CSS_SELECTOR, "body > main > div.relative.-mt-14 > div > div > button"),
        "form_locator": (By.ID,"Download Sub category List"),
        "submit_button": (By.CSS_SELECTOR, r"#Download\ Sub\ category\ List > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"},
        "fields": { 
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 11. Side by Side Comparison Form (Single-step)
    {
        "form_type": "Side by Side Comparison",
        "page_url": "https://softwarefinder.com/resources/blackboard-vs-canvas-comparison",
        "access_method": "direct",
        "form_locator": (By.ID,"Side-by-Side Review"),
        "submit_button": (By.CSS_SELECTOR, r"#Side-by-Side\ Review > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 12. Download Whitepaper Form (Single-step)
    {
        "form_type": "Download Whitepaper",
        "page_url": "https://softwarefinder.com/resources/5-top-rated-payroll-software-for-small-businesses",
        "access_method": "direct",
        "form_locator": (By.ID,"Download Whitepaper"),
        "submit_button": (By.CSS_SELECTOR, r"#Download\ Whitepaper > div > div > button"),
        "success_condition": {"type": "redirect", "url_contains": "resources/other-files"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 13. Webinar on Demand Registration (Single-step)
    {
        "form_type": "Webinar on Demand Registration",
        "page_url": "https://softwarefinder.com/resources/building-a-resilient-workforce-ai-driven-hr-tools-for-recruitment-and-performance-tracking",
        "access_method": "direct",
        "form_locator": (By.ID,"On-Demand Software Review"),
        "submit_button": (By.XPATH , "//*[@id='On-Demand Software Review']/button"),
        "success_condition": {"type": "form_cleared"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 14. Webinar on Demand Watch (Single-step)
    {
        "form_type": "Webinar on Demand Watch",
        "page_url": "https://softwarefinder.com/resources/ol-2-regulatory-compliance-new-medical-practices",
        "access_method": "direct",
        "form_locator": (By.ID,"On-Demand Software Review"),
        "submit_button": (By.XPATH, "//*[@id='On-Demand Software Review']/button"),
        "success_condition": {"type": "form_cleared"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 15. Feeling Overwhelmed By Options Listed (Single-step)
    {
        "form_type": "Feeling Overwhelmed By Options Listed",
        "page_url": "https://softwarefinder.com/retail",
        "access_method": "direct",
        "form_locator": (By.ID,"Feeling overwhelmed by all the Category option listed"),
        "submit_button": (By.XPATH, "//*[@id='Feeling overwhelmed by all the Category option listed']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 16. Not Sure if Right Fit (Single-step)
    {
        "form_type": "Not Sure if Right Fit",
        "page_url": "https://softwarefinder.com/emr-software/athenahealth",
        "access_method": "direct",
        "form_locator": (By.ID,"Not sure if Vendor is the right fit?"),
        "submit_button": (By.XPATH, "//*[@id='Not sure if Vendor is the right fit?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 17. Need Help Finding (Single-step)
    {
        "form_type": "Need Help Finding",
        "page_url": "https://softwarefinder.com/emr-software",
        "access_method": "direct",
        "form_locator": (By.ID, "Need Help Finding Category Software"),
        "submit_button": (By.XPATH, "//*[@id='Need Help Finding Category Software']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 18. Need Help Deciding? (Single-step)
    {
        "form_type": "Need Help Deciding?",
        "page_url": "https://softwarefinder.com/",
        "access_method": "direct",
        "form_locator": (By.ID,"Need help deciding ?"),
        "submit_button": (By.XPATH, "//*[@id='Need help deciding ?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 19. Looking for Software? (Single-step)
    {
        "form_type": "Looking for Software?",
        "page_url": "https://softwarefinder.com/resources",
        "access_method": "direct",
        "form_locator": (By.ID, "Looking for Software?"),
        "submit_button": (By.XPATH, "//*[@id='Looking for Software?']/div/div/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
    # 20. Message Us (Single-step)
    {
        "form_type": "Message Us",
        "page_url": "https://softwarefinder.com/contact-us",
        "access_method": "direct",
        "form_locator": (By.ID, "Message Us"),
        "submit_button": (By.XPATH, "//*[@id='Message Us']/div/div[3]/button"),
        "success_condition": {"type": "redirect", "url_contains": "thank-you?type=recommendation"},
        "fields": {
            "name": {
                "value": "Test User",
                "type": "text",
                "selectors": ["[name='name']", "#name"]
            },
            "phone": {
                "value": "+1-234-567-8900",
                "type": "phone",
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
            },
            "Message": {
                "value": "Test Message 123",
                "type": "textarea",
                "selectors": ["[name='Message']", "#Message"]
            }
        }
    }
]

class FormTester:
    def __init__(self, browser='chrome', headless=True):
        self.browser = browser.lower()
        self.results = []
        
        if self.browser == 'chrome':
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--window-size=1920,1080")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-dev-shm-usage")
            self.driver = webdriver.Chrome(
                service=ChromeService(ChromeDriverManager().install()),
                options=options
            )
        elif self.browser == 'firefox':
            options = webdriver.FirefoxOptions()
            if headless:
                options.add_argument("--headless")
            options.add_argument("--width=1920")
            options.add_argument("--height=1080")
            self.driver = webdriver.Firefox(
                service=FirefoxService(GeckoDriverManager().install()),
                options=options
            )
        else:
            raise ValueError(f"Unsupported browser: {browser}")

        self.wait = WebDriverWait(self.driver, 30)
        self.actions = ActionChains(self.driver)
        logger.info(f"Initialized {browser} WebDriver in {'headless' if headless else 'headed'} mode")

    def find_element_by_selectors(self, parent, selectors):
        """Try multiple selectors to find an element"""
        for selector in selectors:
            try:
                element = parent.find_element(By.CSS_SELECTOR, selector)
                if element.is_displayed():
                    logger.info(f"Found element using selector: {selector}")
                    return element
            except NoSuchElementException:
                continue
        return None

    def find_button(self, config):
        """Find and return the form button"""
        self.driver.get(config["page_url"])
        self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        logger.info(f"Current URL: {self.driver.current_url}")

        if config.get("button_locator"):
            try:
                button = self.wait.until(EC.element_to_be_clickable(config["button_locator"]))
                logger.info("Found button with configured locator")
                return button
            except TimeoutException:
                # Fallback: search for common button text or attributes
                common_button_selectors = [
                    (By.XPATH, "//button"),  
                    (By.CSS_SELECTOR, "[type='button']"),
                    (By.XPATH, "//button[contains(text(), 'Get Recommendation')]"),
                    (By.XPATH, "//button[contains(text(), 'Get Pricing')]"),
                    (By.XPATH, "//button[contains(text(), 'Write a Review')]")
                ]
                for selector in common_button_selectors:
                    try:
                        button = self.driver.find_element(*selector)
                        if button.is_displayed():
                            logger.info(f"Found button using fallback selector: {selector}")
                            return button
                    except NoSuchElementException:
                        continue
                raise Exception("Button not found with any locator")

    def fill_text_field(self, element, value):
        """Fill a text or textarea field"""
        element.clear()
        element.send_keys(value)

    def select_option(self, element, value):
        """Select an option from a dropdown"""
        select = Select(element)
        select.select_by_visible_text(value)

    def set_slider(self, parent, label, value):
        """Set the value of a slider based on its label"""
        try:
            slider = parent.find_element(
                By.XPATH,
                f"//label[contains(text(), '{label}')]/following-sibling::input[@type='range']"
            )
            self.driver.execute_script(
                f"arguments[0].value = {value}; arguments[0].dispatchEvent(new Event('change'));",
                slider
            )
            logger.info(f"Set slider '{label}' to value {value}")
        except NoSuchElementException:
            raise Exception(f"Slider for '{label}' not found")

    def set_star_rating(self, selector, value):
        try:
            stars = self.driver.find_elements(*selector)
            if len(stars) < value:
                raise Exception(f"Not enough stars for rating {value}")
            stars[value - 1].click()
            logger.info(f"Set star rating to {value}")
        except NoSuchElementException:
            raise Exception("Star rating elements not found")

    def fill_field(self, parent, field_config):
        """Fill a field based on its type"""
        element = self.find_element_by_selectors(parent, field_config["selectors"])
        if not element:
            raise Exception(f"Field not found: {field_config['selectors']}")
        field_type = field_config["type"]
        value = field_config["value"]
        if field_type in ["text", "email", "phone", "textarea"]:
            self.fill_text_field(element, value)
        elif field_type == "select":
            self.select_option(element, value)
        else:
            raise Exception(f"Unknown field type: {field_type}")

    def check_success(self, success_condition, config):
        """Verify the form submission success condition"""
        if success_condition["type"] == "redirect":
            self.wait.until(EC.url_contains(success_condition["url_contains"]))
            logger.info(f"Success: Redirected to URL containing '{success_condition['url_contains']}'")
        elif success_condition["type"] == "form_cleared":
            self.wait.until_not(EC.presence_of_element_located(config["form_locator"]))
            logger.info("Success: Form cleared or removed")

    def test_form(self, config):
        """Test a single form based on its configuration"""
        test_start = datetime.now()
        result = {
            "form_type": config["form_type"],
            "status": "failure",
            "duration": None,
            "error": None,
            "browser": self.browser,
            "timestamp": test_start.isoformat()
        }

        try:
            self.driver.get(config["page_url"])
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))  # Wait for page load

            # Access the form
            if config["access_method"] == "button":
                button = self.find_button(config)
                button.click()
                self.wait.until(EC.visibility_of_element_located(config["form_locator"]))  # Wait for form to appear
                form = self.wait.until(EC.presence_of_element_located(config["form_locator"]))
            # Handle multi-step or single-step form
            if config.get("is_multi_step"):
                for step in config["steps"]:
                    # Fill standard fields
                    if "fields" in step:
                        for field_name, field_config in step["fields"].items():
                            self.fill_field(form, field_config)
                    # Handle ratings (sliders)
                    if "ratings" in step:
                        for rating in step["ratings"]:
                            self.set_slider(form, rating["label"], rating["value"])
                    # Handle overall star rating
                    if "overall_rating" in step:
                        rating_container = form.find_element(
                            By.CSS_SELECTOR, step["overall_rating"]["selector"]
                        )
                        self.set_star_rating(step["overall_rating"]["selector"], step["overall_rating"]["value"])
                    # Proceed to next step if applicable
                    if "next_button" in step:
                        next_btn = form.find_element(*step["next_button"])
                        self.wait.until(EC.presence_of_element_located(step["wait_for"]))
            else:
                # Single-step form: fill all fields
                for field_name, field_config in config["fields"].items():
                    self.fill_field(form, field_config)

            # Submit the form
            submit_button = form.find_element(*config["submit_button"])
            submit_button.click()

            # Verify success
            self.check_success(config["success_condition"])

            logger.info(f"Form {config['form_type']} submitted successfully")
            self.results.append({"form_type": config["form_type"], "status": "success"})
            result["status"] = "success"
        except Exception as e:
            logger.error(f"{config['form_type']} failed: {str(e)}")
            result["error"] = str(e)
        finally:
            result["duration"] = str(datetime.now() - test_start)
            self.results.append(result)

    def run_all_tests(self):
        """Execute all tests and generate report"""
        try:
            for config in form_configs:
                self.test_form(config)
        finally:
            self.generate_report()
            self.driver.quit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", choices=["chrome", "firefox"], default="chrome")
    parser.add_argument("--headed", action="store_true", help="Run in headed mode")
    args = parser.parse_args()

    tester = FormTester(
        browser=args.browser,
        headless=not args.headed
    )
    tester.run_all_tests()