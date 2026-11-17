import json

# Read existing JSON file
with open("data/raw/complaints.json", "r") as file:
    data = json.load(file)

# Check total records
print("Total Records:", len(data))

# Check number of columns
if data:
    print("Total Columns:", len(data[0]))

    print("\nAvailable Columns:")
    for column in data[0].keys():
        print(column)