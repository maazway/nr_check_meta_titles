from playwright.sync_api import sync_playwright
import csv
import sys
import os

def check_bulk_urls(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        urls = [row[0] for row in csv.reader(csvfile) if row]

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        for i, url in enumerate(urls, start=1):
            try:
                print(f"[{i}/{len(urls)}] Checking: {url}")
                page.goto(url, timeout=20000)
                title = page.title()
                if title:
                    results.append((url, "OK", title.strip()))
                    print(f"TITLE: {title.strip()}")
                else:
                    results.append((url, "MISSING", "-"))
                    print("MISSING TITLE")
            except Exception as e:
                results.append((url, "ERROR", "-"))
                print(f"ERROR: {e}")

        browser.close()

    # Buat folder results jika belum ada
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    # Nama file hasil tanpa timestamp
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    outname = os.path.join(results_dir, f"{base_name}_report.csv")

    # Simpan hasil ke file CSV
    with open(outname, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "STATUS", "TITLE"])
        writer.writerows(results)

    print(f"\nSelesai! {len(results)} URL diproses.")
    print(f"Hasil disimpan di '{outname}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_urls.py <csv_file>")
    else:
        check_bulk_urls(sys.argv[1])
