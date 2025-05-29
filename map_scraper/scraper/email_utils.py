import re
import requests
from selenium.webdriver.common.by import By

def extract_email(website_url):
    if website_url == "N/A":
        return ""
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(website_url, headers=headers, timeout=10)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
        return ", ".join(set(emails)) if emails else ""
    except:
        return ""

def extract_emails_from_map_popup(driver):
    emails = []
    try:
        email_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
        for elem in email_elements:
            email = elem.text.strip()
            if re.match(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email):
                emails.append(email)
    except Exception as e:
        print(f"E-posta çıkarma hatası: {e}")
    return emails
