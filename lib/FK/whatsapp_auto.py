import os
import time

import pyperclip
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement

from lib.utils.log import logger

log = logger.get_logger()


def get_web_driver() -> webdriver:
    """
    Initializes the Chrome WebDriver with a Automation user profile to maintain session data.
    
    Returns:
        webdriver: An instance of the Chrome WebDriver with the specified user profile.
    """
    profile_path = os.path.join(os.getcwd(), "Automation_Profile")
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-data-dir={profile_path}")

    return webdriver.Chrome(options=options)

def get_search_box(driver: webdriver) -> WebElement:
    """
    Waits for the WhatsApp Web search box to be present and returns it.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
    
    Returns:
        WebElement: The search box element if found, else None.
    """
    search_box_xpath = '//div[@contenteditable="true"][@data-tab="3"]'
    try:
        search_box = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.XPATH, search_box_xpath))
        )

    except Exception as e:
        log.info("Could not find the search box. WhatsApp may have updated their website code.")
        log.info(f"Error details: {e}")
        
    log.info("Page loaded! Searching for contact...")
    return search_box

def get_contact_chat(driver: webdriver, search_box: WebElement, contact_name: str) -> None:
    """
    Searches for a contact in WhatsApp Web and opens the chat with that contact.
    
    Args:
        driver (webdriver): The Selenium WebDriver instance.
        search_box (WebElement): The search box element where the contact name will be entered.
        contact_name (str): The name of the contact to search for and open the chat with.
    
    Returns:
        None
    """
    search_box.click()
    search_box.click()
    search_box.send_keys(Keys.CONTROL, 'a')
    search_box.send_keys(Keys.BACKSPACE)
    time.sleep(0.5)
    search_box.send_keys(contact_name)
        
    driver.implicitly_wait(1) 
            
    search_box.send_keys(Keys.ENTER)
            
    log.info(f"Chat with {contact_name} opened successfully!")        
    log.info("Waiting for the message box...")

def send_message(driver: webdriver, url_text: str, short_text: str) -> None:
    """
    Sends a message to the currently open chat in WhatsApp Web.
    
    Args:
        driver (webdriver): The Selenium WebDriver instance.
        url_text (str): The URL to be sent in the message.
        short_text (str): The short message text to be sent after the URL.
    
    Returns:
        None
    """
    message_box_xpath = '//*[@id="main"]//footer//div[@contenteditable="true"]'
        
    message_box = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.XPATH, message_box_xpath))
    )
        
    log.info("Found message box!")
    pyperclip.copy(short_text)
        
    message_box.click()
    message_box.send_keys(url_text)
    message_box.send_keys(Keys.SHIFT, Keys.ENTER)
    message_box.send_keys(Keys.SHIFT, Keys.ENTER)
    message_box.send_keys(Keys.CONTROL, 'v')
        
    time.sleep(1) 
        
    message_box.send_keys(Keys.ENTER)
    log.info("Message sent successfully!")

def run(contact_names: list, post_url: str, short_msg: str) -> None:
    driver = get_web_driver()
    driver.get("https://web.whatsapp.com")

    for name in contact_names:
        log.info("Waiting for WhatsApp Web to load...")
        search_box = get_search_box(driver)
        get_contact_chat(driver, search_box, name)
        send_message(driver, post_url, short_msg)

        
    input("Press Enter to close the browser...") 
    driver.quit()

if __name__ == "__main__":
    #It currently works with my personal account. Therefore the name in contact is "Jhallo Mai".
    #Todo: Make it work with FK business account once we have it set up.
    
    CONTACT_NAME = ["Jhallo Mai"]
    INSTAGRAM_POST_URL = "https://www.instagram.com/p/DVJbv2dCDfh/?igsh=MXBpdnYwdmNsNGh0ag=="
    SHORT_MSG = "Unterstützt den Post mit einem Like & Kommentar 💛 Jede Interaktion hilft, die Botschaft weiterzutragen! ✨"

    run(CONTACT_NAME, INSTAGRAM_POST_URL, SHORT_MSG)
