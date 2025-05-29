import os
import time
import re
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium import webdriver
import random

from scraper.email_utils import extract_email, extract_emails_from_map_popup
from scraper.tekeindirme import filter_duplicate_emails

TERMS = ["bilgisayar", "bilişim", "yazılım", "bilgisayar tamir servisi",
         "yazılım danışmanlık", "pos cihazı satıcıları", "sosyal medya ajansı"]

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 ...",
        "Mozilla/5.0 ...",  # (Kısaltıldı, istersen hepsini eklerim)
    ]
    return random.choice(USER_AGENTS)

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    return webdriver.Chrome(options=options)

def get_restaurant_info(driver, link):
    driver.get(link)
    time.sleep(5)
    try:
        name = driver.find_element(By.CSS_SELECTOR, 'h1.DUwDvf').text
    except:
        name = ""
    try:
        address = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Adres')]//div[2]").text
    except:
        address = ""
    try:
        phone = driver.find_element(By.XPATH, "//button[contains(@data-tooltip, 'Telefon')]//div[2]").text
    except:
        phone = ""
    try:
        website = driver.find_element(By.XPATH, "//a[contains(@aria-label, 'Web sitesi')]").get_attribute("href")
    except:
        website = "N/A"

    emails = extract_emails_from_map_popup(driver)
    email = extract_email(website) if website != "N/A" else ""
    if emails:
        email += ", " + ", ".join(emails)

    return {
        "Ad": name,
        "Adres": address,
        "Telefon": phone,
        "E-posta": email,
        "Web Sitesi": website,
        "Google Maps Link": link,
    }

def scroll_to_bottom(driver, container):
    prev_height = -1
    stable_scrolls = 0
    while stable_scrolls < 3:
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
        time.sleep(1.2)
        new_height = driver.execute_script("return arguments[0].scrollHeight", container)
        if new_height == prev_height:
            stable_scrolls += 1
        else:
            stable_scrolls = 0
        prev_height = new_height

def scrape_city_district(driver, city, district):
    location = f"{city} {district}".strip()
    all_links = set()

    for term in TERMS:
        try:
            searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            searchbox.clear()
            searchbox.send_keys(f"{location} {term}")
            searchbox.send_keys(Keys.ENTER)
            time.sleep(4)

            sidebar = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']")))
            scroll_to_bottom(driver, sidebar)

            places = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            for place in places:
                href = place.get_attribute("href")
                if href and "www.google.com/maps/place" in href:
                    all_links.add(href)
        except TimeoutException:
            print(f"{location} - Arama veya liste yüklenemedi.")
            continue

    print(f"{location} - {len(all_links)} sonuç bulundu.")

    with ThreadPoolExecutor(max_workers=3) as executor:
        data = list(executor.map(lambda link: get_restaurant_info(driver, link), all_links))

    os.makedirs("outputs", exist_ok=True)
    filename = f"outputs/{city}_{district or 'genel'}.csv"
    pd.DataFrame(data).to_csv(filename, index=False, encoding="utf-8")
    print(f"{filename} kaydedildi.\n")

def run_scraper_gui_input(cities: str, districts: str):
    cities = cities.strip().split(",")
    districts = districts.strip().split(",") if districts else [""] * len(cities)

    if len(cities) != len(districts):
        raise ValueError("Şehir ve ilçe sayısı eşleşmiyor!")

    start_time = time.time()
    driver = get_driver()
    driver.get("https://www.google.com/maps")
    time.sleep(3)

    for city, district in zip(cities, districts):
        scrape_city_district(driver, city.strip(), district.strip())

    driver.quit()
    total_time = time.time() - start_time
    print(f"Toplam süre: {total_time:.2f} saniye")

    csv_file = f"outputs/{cities[0]}_{districts[0] or 'genel'}.csv"
    filter_duplicate_emails(csv_file)
