import re
import random
import json
import os
import pytz
from datetime import datetime
from faker import Faker
from config import STATE_TIMEZONES

fake = Faker()

def load_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file]

def generate_password():
    return fake.password(length=7, special_chars=False).capitalize() + "@"

def generate_email(username):
    email_username = f"{username}{random.randint(100, 999)}"
    return f"{email_username}@gmail.com"

def validate_email(email):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(email_regex, email) is not None

def generate_user_agent():
    user_agents = load_file('../data/user_agents.txt')
    return random.choice(user_agents)

def get_current_time(state):
    timezone = STATE_TIMEZONES.get(state, 'America/New_York')
    tz = pytz.timezone(timezone)
    now = datetime.now(tz)
    return now.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)')

def save_address_info(address_info):
    filename = '../data/addresses.json'
    max_entries = 1000
    addresses = {}

    if os.path.isfile(filename):
        with open(filename, 'r') as file:
            try:
                addresses = json.load(file)
                if isinstance(addresses, list):
                    addresses = {str(i+1): addr for i, addr in enumerate(addresses)}
            except json.JSONDecodeError:
                pass

    if addresses:
        max_number = max(int(key) for key in addresses.keys())
        next_number = max_number + 1 if max_number < max_entries else 1
    else:
        next_number = 1

    addresses[next_number] = address_info

    with open(filename, 'w') as file:
        json.dump(addresses, file, indent=4)

def generate_display_info(state):
    width = random.randint(800, 1920)
    height = random.randint(600, 1080)
    depths = [24, 32, 16]  # Variant desktop values for color depth
    depth = random.choice(depths)
    timezone = -360
    user_agent = generate_user_agent()
    state_timezone = STATE_TIMEZONES.get(state, 'Asia/Bangkok')
    tz = pytz.timezone(state_timezone)
    now = datetime.now(tz)
    isc_time = now.strftime('%a %b %d %Y %H:%M:%S GMT%z (%Z)')

    display_info = {
        "width": width,
        "height": height,
        "depth": depth,
        "timezone": timezone,
        "user_agent": user_agent,
        "current_time": isc_time
    }

    return display_info

def generate_random_string(state, states_to_search):
    return f"{state}{random.choice(states_to_search)}{random.randint(1000, 9999)}"

def is_valid_address_item(item):
    required_fields = ['Street', 'BuildingNumber', 'City', 'ProvinceName', 'Province', 'PostalCode']
    return all(field in item for field in required_fields)