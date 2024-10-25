from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import requests
load_dotenv()

GITHUB_TOKEN = os.getenv('GITHUB_TOKEN_A')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def check_rate_limit():
    response = requests.get('https://api.github.com/rate_limit', headers=HEADERS)
    if response.status_code == 200:
        rate_limit_info = response.json()
        core_reset = rate_limit_info['rate']['reset']
        remaining_requests = rate_limit_info['rate']['remaining']
        reset_time_utc = datetime.utcfromtimestamp(core_reset)
        reset_time_local = reset_time_utc - timedelta(hours=3)
        print(f'Core Rate Limit: 5000')
        print(f'Remaining Requests: {remaining_requests}')
        print(f'Rate Limit Resets At: {reset_time_local.strftime("%Y-%m-%d %H:%M:%S")} BRT')
    else:
        print(f'Erro ao verificar limite de requisições: {response.status_code}')


if __name__ == '__main__':
    check_rate_limit()
