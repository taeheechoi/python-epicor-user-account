import os
import csv
import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()

epicor_api_url = os.getenv('EPICOR_API_URL')
epicor_user_id = os.getenv('EPICOR_USER_ID')
epicor_password = os.getenv('EPICOR_PASSWORD')
company_domain = os.getenv('COMPANY_DOMAIN')


def read_csv_file(file_path):
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row
        yield from reader


def generate_user_id(employee):
    first_name, last_name = employee
    epicor_id = f'{first_name[:1]}{last_name}'.lower()
    return epicor_id


def send_data_to_epicor(endpoint, data, method):
    url = f'{epicor_api_url}/{endpoint}'

    headers = {
        'Content-Type': 'application/json'
    }

    auth = HTTPBasicAuth(epicor_user_id, epicor_password)

    if method == 'POST':
        response = requests.post(url, auth=auth, json=data, headers=headers)
    elif method == 'PATCH':
        response = requests.patch(url, auth=auth, json=data, headers=headers)
    else:
        raise ValueError(
            "Invalid HTTP method. Supported methods are 'POST' and 'PATCH'.")

    response.raise_for_status()

    return response.json()


def create_user_account(employee):
    url = 'Ice.BO.UserFileSvc/UserFiles'

    user_id = generate_user_id(employee)

    user_file = {
        'UserID': user_id,
        'Name': ' '.join(employee),
        'EMailAddress': f'{user_id}@{company_domain}'
    }

    send_data_to_epicor(url, user_file, 'POST')


def inactivate_user_account(employee):
    user_id = generate_user_id(employee)

    url = f'Ice.BO.UserFileSvc/UserFiles({user_id})'

    user_file = {
        'UserID': user_id,
        'UserDisabled': True
    }

    send_data_to_epicor(url, user_file, 'PATCH')


if __name__ == '__main__':
    new_employees = read_csv_file('./data/new-employees.csv')

    for new_employee in new_employees:
        create_user_account(new_employee)

    inactive_employees = read_csv_file('./data/inactive-employees.csv')

    for inactive_employee in inactive_employees:
        inactivate_user_account(inactive_employee)
