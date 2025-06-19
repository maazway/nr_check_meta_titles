import csv
import os

def split_csv(input_file, num_parts=4):
    with open(input_file, newline='', encoding='utf-8') as infile:
        rows = list(csv.reader(infile))

    size = len(rows) // num_parts

    # Buat folder parts jika belum ada
    os.makedirs("parts", exist_ok=True)

    for i in range(num_parts):
        start = i * size
        end = None if i == num_parts - 1 else (i + 1) * size
        output_path = os.path.join("parts", f"urls_part{i+1}.csv")
        with open(output_path, "w", newline='', encoding='utf-8') as outfile:
            writer = csv.writer(outfile)
            writer.writerows(rows[start:end])

    print(f"{num_parts} file telah dibuat di folder 'parts/'")

if __name__ == "__main__":
    split_csv("full_article_link.csv", 4)  # Ganti dengan jumlah part yang diinginkan
