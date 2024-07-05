import requests
from database import save_data_to_db
from database import get_vacancies

def fetch_hh_data(endpoint):
    base_url = "https://api.hh.ru/"
    url = base_url + endpoint

    all_items = []
    page = 0
    per_page = 100

    params = {}
    params['page'] = page
    params['per_page'] = per_page
    while True:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            if not items:
                break
            all_items.extend(items)
            params['page'] += 1
        else:
            break
    save_data_to_db(all_items)

def fetch_db_data(filters=None):
    return get_vacancies(filters=filters)
    
'''    
# Define the API endpoint
url = "https://api.hh.ru/vacancies"

# Set parameters for the request
params = {
    'text': 'Python developer',  # Search query
    'area': '1',  # Region (1 - Moscow)
    'per_page': '10',  # Number of results per page
    'page': '0'  # Page number
}

# Make the GET request
response = requests.get(url, params=params)

# Check the status code of the response
if response.status_code == 200:
    # Parse the JSON response
    data = response.json()
    
    # Print the data (for demonstration purposes)
    for vacancy in data['items']:
        print(f"Vacancy: {vacancy['name']}")
        print(f"Employer: {vacancy['employer']['name']}")
        print(f"URL: {vacancy['alternate_url']}")
        print('-' * 40)
else:
    print(f"Failed to fetch data: {response.status_code}")
''' 

