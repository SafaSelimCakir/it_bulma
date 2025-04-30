import pandas as pd
import os

def filter_duplicate_emails():
    csv_file = input("Filtrelemek istediğiniz CSV dosyasının adını girin (outputs klasöründe olmalı): ")

    csv_path = os.path.join("outputs", csv_file)

    if not os.path.exists(csv_path):
        print(f"Hata: {csv_file} dosyası 'outputs' klasöründe bulunamadı!")
        return
    
    df = pd.read_csv(csv_path)

    print("CSV Dosyasındaki Sütunlar:")
    print(df.columns)

    if "E-posta" not in df.columns:
        print("Hata: CSV dosyasında 'E-posta' sütunu bulunamadı!")
        return


    df = df.drop_duplicates(subset="Ad", keep="first")

    output_dir = "filtrelenmis_data"
    os.makedirs(output_dir, exist_ok=True)

    new_file_name = f"filtreli_{os.path.splitext(csv_file)[0]}.csv"
    new_csv_path = os.path.join(output_dir, new_file_name)

    df.to_csv(new_csv_path, index=False, encoding="utf-8")

    print(f"\nGüncellenmiş veriler '{new_csv_path}' olarak kaydedildi!")

filter_duplicate_emails()
