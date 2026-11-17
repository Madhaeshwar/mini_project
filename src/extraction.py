
import requests
import pandas as pd
import time
import os

url = "https://data.cityofnewyork.us/resource/erm2-nwe9.json"

fields = "unique_key,created_date,closed_date,due_date,agency,agency_name,complaint_type,descriptor,borough,status,latitude,longitude,location_type,incident_zip,incident_address,street_name,cross_street_1,cross_street_2,resolution_description,community_board,council_district,police_precinct,open_data_channel_type,bbl,landmark"

limit = 1000
max_records = 100000

# Read existing CSV
file_path = "data/raw/complaints.csv"
df = pd.read_csv(file_path)

offset = len(df)

print("Existing Records:", offset)

# Continue extraction
while offset < max_records:

    params = {
        "$select": fields,
        "$where": "created_date >= '2020-01-01T00:00:00'",
        "$order": "unique_key",
        "$limit": limit,
        "$offset": offset
    }

    data = None

    # Retry handling
    for attempt in range(3):
        try:
            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()
            data = response.json()
            break

        except requests.exceptions.RequestException as e:
            print("API Error:", e)
            print("Retrying...")
            time.sleep(5)

    if data is None or len(data) == 0:
        print("Extraction stopped.")
        break

    # Match existing CSV columns
    new_df = pd.DataFrame(data).reindex(columns=df.columns)

    new_df.to_csv(file_path, mode="a", header=False, index=False)

    offset += len(data)

    print("Total Records:", offset)

    if len(data) < limit:
        break

    time.sleep(2)

print("\nExtraction Finished!")
print("Total Records:", offset)
