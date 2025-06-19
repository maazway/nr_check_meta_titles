import csv
import glob
import os

def merge_reports(output_file="all_urls_report.csv"):
    report_files = sorted(glob.glob("results/urls_part*.csv"))
    all_rows = []

    for file in report_files:
        print(f"Membaca: {file}")
        with open(file, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Lewati header
            all_rows.extend(reader)

    with open("results/" + output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "STATUS", "TITLE"])
        writer.writerows(all_rows)

    print(f"\nGabungan selesai. Hasil: 'results/{output_file}' ({len(all_rows)} baris)")

if __name__ == "__main__":
    merge_reports()
