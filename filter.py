import pandas as pd
import os

blacklist_domains = ["sentry.wixpress.com", "sentry-next.wixpress.com", "sentry.io" ,"jpg" ,"png", "support.yandex.ru" ,"yandex" 
                     ,"yakalamac" ,"addresshere","Sb","fb","example","mapquest","evendo","surecart","micahrich","polyfill",
                     "core-js-bundle@3.2.1", "react@18.3.1","info@fenerbahcetodori.com", "lodash@4.17.21, react-dom@18.3.1",
                     "lodash@4.17.21"," react-dom@18.3.1","dave@lab6.com"," typesetit@att.net", "hi@typemade.mx","readmore-js@2.2.1",
                     "chart.js@4.4.7", "bootstrap@5.3.3", "i18next@24.2.1, axios@1.7.9","i18next@24.2.1", "axios@1.7.9","bootstrap@4.6.2",
                     "bootstrap","leaflet","fancybox","wght","popup","aos","react-dom","select2"]

email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

def is_valid_email(email):
    return not any(domain in email for domain in blacklist_domains)

def filter_wixpress_emails(email_str):
    if pd.isna(email_str):  
        return ""
    
    filtered_emails = [
        email.strip() for email in email_str.split(",") 
        if not any(domain in email for domain in blacklist_domains)
    ]
    
    return ", ".join(filtered_emails) if filtered_emails else ""

def filter_no_email_entries():
    csv_file = input("Filtrelemek istediğiniz CSV dosyasının adını girin (outputs klasöründe olmalı): ")

    csv_paths = [
        os.path.join("outputs", csv_file)
    ]

    csv_path = next((path for path in csv_paths if os.path.exists(path)), None)

    if not csv_path:
        print(f"Hata: {csv_file} dosyası 'outputs' klasörinde bulunamadı!")
        return
    
    df = pd.read_csv(csv_path)

    print("CSV Dosyasındaki Sütunlar:")
    print(df.columns)

    if "E-posta" not in df.columns:
        print("Hata: CSV dosyasında 'E-posta' sütunu bulunamadı!")
        return

    df_filtered = df[df["E-posta"].notna() & 
                     (df["E-posta"] != "No Email Found") & 
                     (df["E-posta"] != "Error Accessing Site") &  
                     (df["E-posta"] != "No Website")]

    df_filtered["E-posta"] = df_filtered["E-posta"].apply(filter_wixpress_emails)

    df_filtered = df_filtered[df_filtered["E-posta"] != ""]

    # Aynı restoran adını taşıyan kayıtları teke indir
    df_filtered = df_filtered.drop_duplicates(subset="Ad", keep="first")

    invalid_emails = df_filtered[~df_filtered["E-posta"].astype(str).str.match(email_regex, na=False)]

    print("\nGeçersiz e-posta formatında olanlar:")
    print(invalid_emails)

    output_dir = "filtrelenmis_data"
    os.makedirs(output_dir, exist_ok=True)

    new_file_name = f"filtreli_{os.path.splitext(csv_file)[0]}.csv"
    new_csv_path = os.path.join(output_dir, new_file_name)

    df_filtered.to_csv(new_csv_path, index=False, encoding="utf-8")

    print(f"\nGüncellenmiş veriler '{new_csv_path}' olarak kaydedildi! (Geçersiz e-posta adresleri çıkarıldı)")

filter_no_email_entries()
