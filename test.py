import json

with open('locations.json', encoding="utf-8") as f:
    data = json.load(f)
    print(data["locations"]["bdl"]["vpr"].dict_keys())