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
import requests
from django.conf import settings
from .models import ScrapeRequest

# Keyword mapping: main keywords to sub-keywords
KEYWORD_MAPPING = {
    'restoran': [
        'kebapçı', 'pideci', 'balık restoranı', 'fast food', 'vegan restoran',
        'kahvaltı mekanı', 'ızgara restoran', 'çiğ köfteci', 'et lokantası',
        'pizza restoranı', 'tatlıcı', 'dönerci', 'büfe'
    ],
    'kafe': [
        'kahve dükkanı', 'nargile kafe', 'kitap kafe', 'internet kafe',
        'oyun kafe', 'çay bahçesi', 'butik kafe', 'pastane'
    ],
    'teknik servis': [
        'telefon tamiri', 'bilgisayar tamiri', 'beyaz eşya servisi',
        'klima servisi', 'televizyon tamiri', 'elektronik eşya servisi'
    ],
    'oto tamir': [
        'oto elektrik', 'oto kaporta', 'oto boya', 'oto lastikçi',
        'oto klima', 'egzoz tamiri', 'araç yıkama', 'araç bakım servisi'
    ],
    'market': [
        'süpermarket', 'bakkal', 'manav', 'şarküteri', 'organik ürün mağazası'
    ],
    'mağaza': [
        'elektronik mağaza', 'giyim mağazası', 'ayakkabı mağazası', 'oyuncakçı',
        'kitapçı', 'takı mağazası', 'yapı market', 'mobilya mağazası',
        'ev dekorasyon mağazası'
    ],
    'kuaför': [
        'erkek kuaförü', 'kadın kuaförü', 'berber', 'çocuk kuaförü'
    ],
    'güzellik salonu': [
        'cilt bakımı', 'masaj salonu', 'manikür & pedikür', 'epilasyon merkezi',
        'solaryum', 'kaş & kirpik uygulamaları'
    ],
    'sağlık merkezi': [
        'diş kliniği', 'özel hastane', 'devlet hastanesi', 'veteriner kliniği',
        'optik', 'psikolog', 'fizik tedavi merkezi', 'tıp merkezi',
        'aile sağlığı merkezi', 'diyetisyen', 'eczane'
    ],
    'otel': [
        'butik otel', 'pansiyon', 'apart otel', 'hostel', 'dağ evi',
        'bungalov', 'kamp alanı', 'tatil köyü', 'motel'
    ],
    'okul': [
        'anaokulu', 'ilkokul', 'lise', 'özel okul', 'etüt merkezi',
        'kurs merkezi', 'dil okulu', 'sürücü kursu', 'müzik okulu', 'üniversite'
    ],
    'banka': [
        'ATM', 'şube', 'döviz bürosu'
    ],
    'kamu kurumu': [
        'belediye', 'tapu müdürlüğü', 'nüfus müdürlüğü', 'noter',
        'vergi dairesi', 'emniyet müdürlüğü', 'postane'
    ],
    'benzin istasyonu': [
        'LPG istasyonu', 'elektrikli araç şarj noktası'
    ],
    'araç hizmetleri': [
        'oto kiralama', 'oto yıkama', 'otopark', 'oto aksesuar', 'yol yardım'
    ]
}

# Blacklist domains for email filtering
BLACKLIST_DOMAINS = [
    "sentry.wixpress.com", "sentry-next.wixpress.com", "sentry.io", "jpg", "png",
    "support.yandex.ru", "yandex", "yakalamac", "addresshere", "Sb", "fb", "example",
    "mapquest", "evendo", "surecart", "micahrich", "polyfill", "core-js-bundle@3.2.1",
    "react@18.3.1", "info@fenerbahcetodori.com", "lodash@4.17.21", "react-dom@18.3.1",
    "dave@lab6.com", "typesetit@att.net", "hi@typemade.mx", "readmore-js@2.2.1",
    "chart.js@4.4.7", "bootstrap@5.3.3", "i18next@24.2.1", "axios@1.7.9",
    "bootstrap@4.6.2", "leaflet", "fancybox", "wght", "popup", "aos", "select2"
]

EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def get_random_user_agent():
    USER_AGENTS = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.864.64 Safari/537.36 Edge/91.0.864.64",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 OPR/77.0.4054.172",
        "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.200205.003; wv) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36"
    ]
    return random.choice(USER_AGENTS)

def get_driver():
    options = webdriver.ChromeOptions()
    options.add_argument(f"user-agent={get_random_user_agent()}")
    options.add_argument("--disable-gpu")
    options.add_argument("--start-maximized")
    #options.add_argument("--headless=new")
    return webdriver.Chrome(options=options)

def extract_email(website_url):
    if website_url == "N/A":
        return ""
    try:
        headers = {"User-Agent": get_random_user_agent()}
        response = requests.get(website_url, headers=headers, timeout=10)
        emails = re.findall(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", response.text)
        return ", ".join(set(emails)) if emails else ""
    except:
        return ""

def extract_emails_from_map_popup(driver):
    emails = []
    try:
        email_elements = driver.find_elements(By.XPATH, "//*[contains(text(), '@')]")
        for email_element in email_elements:
            email = email_element.text.strip()
            if re.match(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+", email):
                emails.append(email)
    except Exception as e:
        print(f"Error extracting emails from popup: {e}")
    return emails

def get_place_info(driver, link):
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
        email += ", " + ", ".join(emails) if email else ", ".join(emails)
    
    return {
        "Name": name,
        "Address": address,
        "Phone": phone,
        "Email": email,
        "Website": website,
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

def filter_wixpress_emails(email_str):
    if pd.isna(email_str):
        return ""
    
    filtered_emails = [
        email.strip() for email in email_str.split(",")
        if email.strip() and not any(domain in email for domain in BLACKLIST_DOMAINS)
        and re.match(EMAIL_REGEX, email.strip())
    ]
    
    return ", ".join(filtered_emails) if filtered_emails else ""

def apply_custom_filter(df, column=None, value=None):
    """Apply custom filter to DataFrame based on user input."""
    if column and value and column in df.columns:
        if column == "Email":
            # Apply email-specific filtering
            df = df[df["Email"].notna() & 
                    (df["Email"] != "No Email Found") & 
                    (df["Email"] != "Error Accessing Site") & 
                    (df["Email"] != "No Website") & 
                    (df["Email"] != "")]
            df["Email"] = df["Email"].apply(filter_wixpress_emails)
            df = df[df["Email"] != ""]
            # Additional filter by value if provided
            if value:
                df = df[df["Email"].astype(str).str.contains(value, case=False, na=False)]
        else:
            # Generic filter for other columns
            df = df[df[column].astype(str).str.contains(value, case=False, na=False)]
    return df

def filter_data(df, column=None, value=None):
    """Apply default and custom filters to DataFrame."""
    # Default filter: Remove duplicates based on 'Name' (instead of 'Ad')
    if 'Name' in df.columns:
        df = df.drop_duplicates(subset="Name", keep="first")
    
    # Remove rows with empty 'Name' or 'Address'
    df = df[df['Name'].notna() & (df['Name'] != '')]
    df = df[df['Address'].notna() & (df['Address'] != '')]
    
    # Apply custom filter if provided
    df = apply_custom_filter(df, column, value)
    
    return df

def scrape_location(user, country, city, category, filter_column=None, filter_value=None):
    location = f"{country} {city or ''}".strip()
    driver = get_driver()
    driver.get("https://www.google.com/maps")
    time.sleep(3)
    all_links = set()
    
    # Get the main keyword and its sub-keywords
    search_terms = [category]
    if category in KEYWORD_MAPPING:
        search_terms.extend(KEYWORD_MAPPING[category])

    for term in search_terms:
        try:
            searchbox = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "searchboxinput")))
            searchbox.clear()
            search_query = f"{location} {term}"
            print(f"Searching for: {search_query}")
            searchbox.send_keys(search_query)
            searchbox.send_keys(Keys.ENTER)
            time.sleep(4)

            sidebar = WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div[role='feed']"))
            )
            scroll_to_bottom(driver, sidebar)

            places = driver.find_elements(By.CSS_SELECTOR, "a.hfpxzc")
            for place in places:
                href = place.get_attribute("href")
                if href and "www.google.com/maps/place" in href:
                    all_links.add(href)
        except TimeoutException:
            print(f"Timeout for {location} - {term}")
            continue

    print(f"Found {len(all_links)} unique links for {location} - {category}")

    def fetch_info(link):
        return get_place_info(driver, link)

    with ThreadPoolExecutor(max_workers=3) as executor:
        data = list(executor.map(fetch_info, all_links))

    driver.quit()

    if not data:
        print(f"No data scraped for {location} - {category}")
        return None

    # Convert to DataFrame and apply filters
    df = pd.DataFrame(data)
    df = filter_data(df, column=filter_column, value=filter_value)

    if df.empty:
        print(f"No data after filtering for {location} - {category}")
        return None

    # Generate CSV
    os.makedirs(os.path.join(settings.MEDIA_ROOT, 'csv_files'), exist_ok=True)
    filename = f"{country}_{city or 'general'}_{category.replace(' ', '_')}_{int(time.time())}.csv"
    filepath = os.path.join(settings.MEDIA_ROOT, 'csv_files', filename)
    df.to_csv(filepath, index=False, encoding="utf-8")
    print(f"Saved CSV to {filepath}")

    # Save ScrapeRequest
    scrape_request = ScrapeRequest.objects.create(
        user=user if user.is_authenticated else None,
        country=country,
        city=city,
        category=category,
        filter_column=filter_column,
        filter_value=filter_value,
        csv_file=f"csv_files/{filename}"
    )

    return filename