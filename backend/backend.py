import requests
from database import save_data_to_db
from database import get_vacancies
import pandas as pd

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
    #if not get_vacancies():
    #    fetch_hh_data("vacancies")
    return get_vacancies(filters=filters)
    
def export_vacancies_to_excel(vacancies, file_path='vacancies.xlsx'):
    data = [{
        'ID': v.id,
        'Name': v.name,
        'Employer': v.employer_name,
        'Area': v.area,
        'URL': v.url
    } for v in vacancies]
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)