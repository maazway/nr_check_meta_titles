# scripts/check_full_article_link.py
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import csv
import sys
import os
from dotenv import load_dotenv

load_dotenv()

def extract_title_from_html(html):
    start = html.find("<title>")
    end = html.find("</title>")
    if start != -1 and end != -1:
        return html[start + 7:end].strip()
    return "-"

def check_bulk_urls(file_path):
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        urls = [row[0] for row in csv.reader(csvfile) if row]

    results = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-infobars',
            '--no-sandbox',
            '--disable-dev-shm-usage'
        ])
        context = browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1280, "height": 800},
            java_script_enabled=True,
            is_mobile=False,
            has_touch=False,
            device_scale_factor=1
        )

        page = context.new_page()

        # Tambahkan stealth JS (anti bot detection)
        page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'languages', {get: () => ['en-US', 'en']});
            Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
            window.chrome = { runtime: {} };
        """)

        for i, url in enumerate(urls, start=1):
            try:
                print(f"[{i}/{len(urls)}] Checking: {url}")
                page.goto(url, timeout=30000, wait_until="domcontentloaded")

                # Simulasikan interaksi manusia
                page.mouse.move(200, 200)
                page.wait_for_timeout(1000)
                page.mouse.click(300, 300)
                page.wait_for_timeout(500)
                page.keyboard.press("ArrowDown")
                page.wait_for_timeout(3000)

                try:
                    page.wait_for_function("() => document.title && document.title.length > 0", timeout=10000)
                except:
                    pass

                title = page.title().strip()

                if not title or "403" in title or "forbidden" in title.lower():
                    html = page.content()
                    title = extract_title_from_html(html)

                if title and title != "-" and "403" not in title.lower():
                    results.append((url, "OK", title))
                    print(f"TITLE: {title}")
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
