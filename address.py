import aiohttp
import random
import logging
from config import NEAREST_STATES
from utils import load_file, generate_random_string, is_valid_address_item

API_KEYS = load_file('api_keys.txt')
current_api_key_index = 0
api_key_exceeded = [False] * len(API_KEYS)

async def get_address(state):
    global current_api_key_index
    max_attempts = len(API_KEYS) * 2

    states_to_search = [state] + NEAREST_STATES.get(state, [])
    logging.debug(f"States to search: {states_to_search}")

    async with aiohttp.ClientSession() as session:
        for attempt in range(max_attempts):
            random_string = generate_random_string(state, states_to_search)
            logging.debug(f"Generated random string for attempt {attempt}: {random_string}")
            url = f"https://api.addressy.com/Capture/Interactive/Find/v1.1/json3.ws?Key={API_KEYS[current_api_key_index]}&Text={random_string}&Origin=US&Countries=US&Language=en-gb"
            async with session.get(url, ssl=False) as response:
                response_json = await response.json()

            if response_json['Items'][0].get('Error') == "17":
                api_key_exceeded[current_api_key_index] = True
                current_api_key_index = (current_api_key_index + 1) % len(API_KEYS)
                if all(api_key_exceeded):
                    return None
                continue

            address_item = next((item for item in response_json['Items'] if item['Type'] == 'Address'), None)
            if not address_item:
                continue

            url2 = f"https://api.addressy.com/Capture/Interactive/Retrieve/v1/json3.ws?Key={API_KEYS[current_api_key_index]}&Id={address_item['Id']}"
            async with session.get(url2, ssl=False) as response2:
                response2_json = await response2.json()
                item = response2_json['Items'][0]

            if is_valid_address_item(item):
                return {
                    'street': item['Street'],
                    'full_address': f"{item['BuildingNumber']} {item['Street']}",
                    'city': item['City'],
                    'state': item['ProvinceName'],
                    'state_short': item['Province'],
                    'zip': item['PostalCode'].split('-')[0]
                }
    return None