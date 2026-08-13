#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 15:16:24 2026

@author: sunnysang
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import time
import pandas as pd
from datetime import datetime

# Fetch current date and time
now = datetime.now()
formatted_time = now.strftime("%Y-%m-%d %I%p").lower()

# --- Step 1: Configure Chrome ---
chrome_options = Options()
chrome_options.add_argument("--headless")  # run without opening a browser window
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)  # Selenium 4+ auto-manages ChromeDriver

# --- Step 2: Scrape Google Trends ---
url = "https://trends.google.com/trending?geo=HK&sort=search-volume"
driver.get(url)
time.sleep(10)  # wait for page to load fully

# Get all rows
# Get all rows in the table
entries = driver.find_elements(By.XPATH, '//*[@id="trend-table"]/div[1]/table/tbody[2]/tr')

trends = []
for entry in entries:
    try:
        # Grab all <td> cells in the row
        cells = entry.find_elements(By.TAG_NAME, "td")

        # Only proceed if we have enough cells
        if len(cells) >= 4:
            title = cells[1].text.strip()          # Column 2 → Title
            search_count = cells[2].text.strip()   # Column 3 → Search count
            elapsed_hours = cells[3].text.strip()  # Column 4 → Elapsed hours

            # Append the tuple for this row
            trends.append((title, search_count, elapsed_hours))

    except Exception as e:
        print("Skipping row due to error:", e)
        continue

driver.quit()

df = pd.DataFrame(trends, columns=["Title", "Search Count", "Elapsed Hours"])

# --- Step 3: Build DataFrame ---
# Limit to 25 rows
df = df.head(25)

# Convert DataFrame to HTML table for email
html_table = df.to_html(index=False, border=1, justify="center")

print(html_table)  # Debug: see the HTML table output

# --- Step 4: Send Email via Gmail ---
sender_email = "stw.dick@gmail.com"
receiver_email = ["wyc_stw@hotmail.com" 
                  ,"stw.dick@gmail.com"
                  #,"Janice.kayic@gmail.com" #-- Ka Yi
                  ,"Py.info@gmail.com"
                 ]
password = "pmomdcchcgpeendn"  # Gmail app password (not your normal login password)

# Create the email
msg = MIMEMultipart("alternative")
msg["Subject"] = f"Latest Google Trends HK Snapshot ({formatted_time})"
msg["From"] = sender_email
msg["To"] = ", ".join(receiver_email)

# Attach the HTML table
html_content = f"""
<html>
  <body>
    <p>Here are the latest Google Trends (HK):</p>
    {html_table}
  </body>
</html>
"""
msg.attach(MIMEText(html_content, "html"))

# Send via Gmail SMTP
with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())


print("Email sent successfully via Gmail!")
