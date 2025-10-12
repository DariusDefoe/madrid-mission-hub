import csv
import re
import os
import pandas as pd
import glob

# Step One: Define input and output files & directories
files = glob.glob('~/Desktop/imports/*.txt')
if os.path.exists(files):
    print( f"⚠️ Sub-directory already exists", files)
else:
    os.mkdir('~/Desktop/imports')

output_file = '~/Desktop/exports/cleaned.csv'

# Step Two: Strip whitespace from data in input file
for file in files:
    with open(file) as f:
        data = [re.sub(r'\s+', ' ', line).strip() for line in f.readlines() if line.strip()]

# Step Three: Find the lines that you require
filtered = []
for line in data:
    if re.search(r'^\d{5}', line):
        filtered.append(line)
print(filtered[:10])
# Step Four: Parse the data into a new frame

# Step Five: Write it to a new .csv file
# if os.path.exists(output_file):
#    print("⚠️ File already exists:", output_file)
# else:
#    with open(output_file, 'w', newline='') as f:
#        writer = csv.writer(f)
#        for line in data:
#            writer.writerow([line])
#    print("✅ Wrote cleaned data to", output_file)