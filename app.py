from flask import Flask, jsonify, request
from faker import Faker
import random
import logging
import os
import re  # Add this import for regex validation
from utils import (
    load_file, generate_password, generate_email, validate_email, 
    generate_user_agent, get_current_time, save_address_info, 
    generate_display_info
)
from address import get_address

app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
fake = Faker()

# Use Railway-injected port or fallback to 3000 for local
port = int(os.environ.get("PORT", 3000))

API_KEYS = load_file('api_keys.txt')
counter = 1

logging.basicConfig(level=logging.DEBUG, format='%(levelname)s - %(message)s')
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

def is_valid_phone(phone):
    pattern = r"^\d{3}[2-9]\d{2}\d{4}$"
    return re.match(pattern, phone) is not None

@app.route('/')
async def generate_user():
    global counter
    max_attempts = 5

    state = request.args.get('state', 'NC')

    for attempt in range(max_attempts):
        try:
            first_name = fake.first_name().lower().replace(r'[^a-z]', '')
            last_name = fake.last_name().lower().replace(r'[^a-z]', '')
            username = f"{first_name}.{last_name}"
            password = generate_password()
            email = generate_email(username)

            while not validate_email(email):
                email = generate_email(username)

            phone = generate_phone_number()

            # Validate the generated phone number
            if not is_valid_phone(phone):
                logging.error(f"Invalid phone number generated: {phone}")
                continue  # Retry if the phone number is invalid

            company = fake.company().lower()
            profession = fake.job().lower()
            guid = fake.uuid4().lower()
            user_agent = generate_user_agent()

            address_info = await get_address(state)
            if not address_info:
                logging.error('Failed to retrieve address')
                return jsonify({'error': 'Failed to retrieve address'}), 500

            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            if client_ip:
                client_ip = client_ip.split(',')[0].strip()

            user = {
                'first_name': first_name,
                'last_name': last_name,
                'username': username,
                'password': password,
                'email': email,
                'phone': phone,
                'company': company,
                'profession': profession,
                'guid': guid,
                'counter': counter,
                'ip': client_ip,
                'user_agent': user_agent,
                'current_time': get_current_time(state),
                **address_info,
                **generate_display_info(state)
            }

            if all(user.values()):
                counter = counter + 1 if counter < 5 else 1
                user_items = list(user.items())
                random.shuffle(user_items)
                shuffled_user = dict(user_items)

                save_address_info(address_info)

                return jsonify(shuffled_user)
        except Exception as e:
            logging.error(f'Error generating user: {e}')
            return jsonify({'error': 'Error generating user'}), 500

    logging.error('Failed to generate user after multiple attempts')
    return jsonify({'error': 'Failed to generate user after multiple attempts'}), 500

def generate_phone_number():
    area_code = f"{random.randint(100, 999)}"
    central_office_code = f"{random.randint(200, 999)}"  # Ensures the second digit is between 2-9
    line_number = f"{random.randint(1000, 9999)}"
    return f"{area_code}{central_office_code}{line_number}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port)
