import pandas as pd

def filter_duplicate_emails(csv_path):
    try:
        df = pd.read_csv(csv_path)
        if "E-posta" not in df.columns:
            print("E-posta sütunu bulunamadı.")
            return

        df["E-posta"] = df["E-posta"].fillna("").apply(lambda x: ", ".join(sorted(set(x.split(", "))) if x else []))
        df.to_csv(csv_path, index=False, encoding="utf-8")
        print(f"Tekil e-postalar filtrelendi: {csv_path}")
    except Exception as e:
        print(f"E-posta filtreleme hatası: {e}")
