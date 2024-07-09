import json


with open('data/country_codes.json', 'r') as f:
    country_codes = json.load(f)
    
def parse_country_code(phone_number: str) -> tuple[str, str]:
    for i in range(4, 0, -1):
        code = phone_number[:i]
        if code in country_codes:
            return country_codes[code], code