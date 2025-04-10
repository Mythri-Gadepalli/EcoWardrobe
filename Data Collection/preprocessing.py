import csv
import shutil
import os

# ---------- Step 1: Copy Myntra.csv to Myntrainfo.csv ----------
source_file = "Myntra.csv"
copy_file = "Myntrainfo.csv"

if os.path.exists(source_file):
    shutil.copyfile(source_file, copy_file)
    print(f"✅ Copied {source_file} → {copy_file}")
else:
    print(f"❌ Source file '{source_file}' not found. Please make sure it exists.")
    exit()

# ---------- Step 2: Read from Myntrainfo.csv and get unique details ----------
seen_details = set()
unique_rows = []

with open(copy_file, mode="r", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    header = next(reader, None)  # Skip header if present
    for row in reader:
        if len(row) < 2:
            continue
        detail = row[1].strip()
        if detail not in seen_details:
            seen_details.add(detail)
            unique_rows.append(detail)

# ---------- Step 3: Write unique details to Myntra_Unique.csv ----------
output_file = "Myntra_Unique.csv"

with open(output_file, mode="w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerow(["ID", "Manufacturer Details"])
    for i, detail in enumerate(unique_rows, start=1):
        writer.writerow([i, detail])

print(f"✅ {len(unique_rows)} unique manufacturer details written to '{output_file}'.")
