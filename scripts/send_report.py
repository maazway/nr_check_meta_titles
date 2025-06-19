import smtplib
from email.message import EmailMessage
import os
import csv
from dotenv import load_dotenv

def parse_report(file_path):
    summary = {
        "OK": 0,
        "MISSING": 0,
        "ERROR": 0
    }

    with open(file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            status = row["STATUS"].strip().upper()
            if status in summary:
                summary[status] += 1

    return summary

def build_email_body(summary):
    total = sum(summary.values())
    body = f"""Laporan hasil pengecekan META TITLES NUTRICLUB dari total {total} URL:

    OK       : {summary['OK']}
    MISSING  : {summary['MISSING']}
    ERROR    : {summary['ERROR']}

    Seluruh hasil lengkap tersedia dalam file CSV terlampir.
    (notes: untuk ERROR terjadi jika URL tidak dapat diakses dalam waktu 10 detik)
    """
    return body

def send_email_report():
    load_dotenv()

    file_path = "results/all_urls_report.csv"
    if not os.path.exists(file_path):
        print("File hasil tidak ditemukan.")
        return

    summary = parse_report(file_path)
    body_text = build_email_body(summary)

    msg = EmailMessage()
    msg['Subject'] = 'Laporan Hasil Pengecekan Meta Title URL'
    msg['From'] = os.getenv('EMAIL_USER')
    recipients = [email.strip() for email in os.getenv('EMAIL_TO').split(",")]
    msg['To'] = ", ".join(recipients)
    msg.set_content(body_text)

    with open(file_path, 'rb') as f:
        msg.add_attachment(f.read(), maintype='text', subtype='csv', filename='all_urls_report.csv')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(os.getenv('EMAIL_USER'), os.getenv('EMAIL_PASS'))
        smtp.send_message(msg)

    print("Email berhasil dikirim ke", os.getenv('EMAIL_TO'))

if __name__ == "__main__":
    send_email_report()
