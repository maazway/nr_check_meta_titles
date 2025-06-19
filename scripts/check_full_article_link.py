from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import sys
import os
import time

def check_bulk_urls(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        urls = [row[0] for row in csv.reader(csvfile) if row]

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800},
            device_scale_factor=1,
            is_mobile=False,
            has_touch=False
        )
        page = context.new_page()
        page.set_extra_http_headers({
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive"
        })

        for i, url in enumerate(urls, start=1):
            try:
                print(f"[{i}/{len(urls)}] Checking: {url}")
                page.goto(url, timeout=25000, wait_until="load")
                time.sleep(2)  # beri waktu JS render jalan
                title = page.title()

                if title and "403" not in title.lower() and "Forbidden" not in title:
                    results.append((url, "OK", title.strip()))
                    print(f"TITLE: {title.strip()}")
                else:
                    results.append((url, "MISSING", "-"))
                    print("MISSING TITLE or BLOCKED")
            except PlaywrightTimeoutError:
                results.append((url, "TIMEOUT", "-"))
                print("TIMEOUT: Halaman terlalu lama dimuat")
            except Exception as e:
                results.append((url, "ERROR", "-"))
                print(f"ERROR: {e}")

        browser.close()

    # Simpan hasil
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    outname = os.path.join(results_dir, f"{base_name}_report.csv")

    with open(outname, "w", newline='', encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "STATUS", "TITLE"])
        writer.writerows(results)

    print(f"\nSelesai! {len(results)} URL diproses.")
    print(f"Hasil disimpan di '{outname}'.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python check_full_article_link.py <csv_file>")
    else:
        check_bulk_urls(sys.argv[1])
