"""
Fetch all metadata from a single publication / conference year.
"""

import sys
import time
import json
import requests

# Load config
cfg = json.load(open('config.json'))

# Load existing file
def load_existing_data(fname):
    try: 
        return json.load(open(fname))
    except FileNotFoundError:
        return {}

def get_start_record(data):
    return 1 if data == {} else data["articles"][-1]["rank"] + 1

def should_terminate(start_record, total_records):
    return total_records is not None and start_record > total_records

def update_start_record(data, start_record, max_record, total_records):
    num_downloaded = data["articles"][-1]["rank"]
    return num_downloaded + 1 \
        if start_record + max_record > total_records and num_downloaded < int(total_records) \
        else start_record + max_record

outfile_name = 'data/' + cfg['outfile'] + '/' + cfg['year'] + '.json'
data = load_existing_data(outfile_name)

# Request parameters
url = "http://ieeexploreapi.ieee.org/api/v1/search/articles"
max_record = 200
params = {
    "publication_title": '"' + cfg['publication_title'] + '"',
    "apikey": cfg['apikey'],
    "max_record": str(max_record),
    "start_year": cfg['year'],
    "end_year": cfg['year']
}

# Request constraints
start_record = get_start_record(data)
total_records = None
sleep_duration = 0.5

# Call API in loop
while not should_terminate(start_record, total_records):
    # Make request
    params["start_record"] = start_record
    print("Requesting...")
    print(params)
    r = requests.get(url, params=params)
    try:
        req_json = r.json()
    except json.decoder.JSONDecodeError as e:
        print(e)
        print(r.text)
        sys.exit(1)

    # Append to existing data
    print("Appending data...")
    if data == {}:
        data = req_json
    else:
        data["articles"] += req_json["articles"]

    # Update loop variables
    total_records = req_json["total_records"]
    start_record = update_start_record(data, start_record, max_record, total_records)
    print("start_record: " + str(start_record))
    time.sleep(sleep_duration)

# Save data
with open(outfile_name, 'w') as outfile:
    json.dump(data, outfile)