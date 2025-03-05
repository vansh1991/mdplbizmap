import requests

def get_n8n_users(api_key, limit=100, include_role=True):
    url = 'https://n8n.mdpl.org.in/api/v1/users'
    headers = {
        'accept': 'application/json',
        'X-N8N-API-KEY': api_key
    }
    params = {
        'limit': limit,
        'includeRole': str(include_role).lower()
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()  
    else:
        response.raise_for_status()  


api_key = 'n8n_api_8b93ac6abd19ec9b66ff74d98a838d9a47237f1fbc6f71a9f4c461f5e1630482aa2a63730e7036d6'
response_data = get_n8n_users(api_key)

print(response_data)
# /home/bizmap/frappe-bench/apps/mdpl/mdpl/mdpl/api/test_api.py