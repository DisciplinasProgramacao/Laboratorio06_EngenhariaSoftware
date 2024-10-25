from dotenv import load_dotenv
import requests
import time
import csv
import os
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from itertools import cycle

load_dotenv()

tokens = [
    os.getenv('GITHUB_TOKEN_A'),
    os.getenv('GITHUB_TOKEN_B'),
    os.getenv('GITHUB_TOKEN_C'),
    os.getenv('GITHUB_TOKEN_D'),
    os.getenv('GITHUB_TOKEN_M'),
]

current_token_index = 0

def get_rate_limit(token):
    headers = {'Authorization': f'token {token}'}
    response = requests.get('https://api.github.com/rate_limit', headers=headers)
    if response.status_code == 200:
        rate_limit_data = response.json()
        remaining = rate_limit_data['resources']['core']['remaining']
        reset_time = rate_limit_data['resources']['core']['reset']
        return remaining, reset_time
    else:
        return 0, None
    
def make_request(url, params=None):
    global current_token_index 

    current_token = tokens[current_token_index]
    remaining_requests, reset_time = get_rate_limit(current_token)

    while remaining_requests == 0:
        print(f'Token {current_token_index + 1} expirado. Tentando próximo token...')
        current_token_index = (current_token_index + 1) % len(tokens)
        current_token = tokens[current_token_index]
        remaining_requests, reset_time = get_rate_limit(current_token)

        if remaining_requests == 0:
            print(f'Todos os tokens expiraram. Esperando até {reset_time} para resetar o limite...')
            wait_time = reset_time - int(time.time()) + 1
            time.sleep(wait_time)
            current_token_index = 0

    headers = {'Authorization': f'token {current_token}'}
    response = requests.get(url, headers=headers, params=params)
    return response

def collect_pr_metrics(repo_full_name):
    pr_data = []
    page = 1
    per_page = 30
    total_pr_count = 0
    while True:
        url = f'https://api.github.com/repos/{repo_full_name}/pulls'
        params = {
            'state': 'closed',
            'sort': 'created',
            'direction': 'desc',
            'per_page': per_page,
            'page': page
        }
        response = make_request(url, params=params)
        print(response)
        if response.status_code != 200:
            print(f'Erro ao obter PRs de {repo_full_name}: {response.status_code}')
            break
        prs = response.json()

        if not prs:
            break
        
        for pr in prs:
            if total_pr_count >= 100:
                break

            if pr['merged_at'] or pr['state'] == 'closed':
                pr_number = pr['number']
                pr_created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                pr_closed_at_str = pr['closed_at'] if pr['closed_at'] else pr.get('merged_at')
                if not pr_closed_at_str:
                    continue
                
                pr_closed_at = datetime.strptime(pr_closed_at_str, '%Y-%m-%dT%H:%M:%SZ')
                duration = pr_closed_at - pr_created_at
                
                if duration >= timedelta(hours=1):
                    files_url = pr['url'] + '/files'
                    files_response = make_request(files_url)
                    if files_response.status_code == 200:
                        files = files_response.json()
                        num_files = len(files)
                        additions = sum([file.get('additions', 0) for file in files])
                        deletions = sum([file.get('deletions', 0) for file in files])
                    else:
                        print(f'Erro ao obter arquivos do PR #{pr_number} em {repo_full_name}: {files_response.status_code}')
                        continue
                    
                    reviews_url = pr['url'] + '/reviews'
                    reviews_response = make_request(reviews_url)
                    if reviews_response.status_code == 200:
                        reviews = reviews_response.json()
                        num_reviews = len(reviews)
                        participants = set()
                        for review in reviews:
                            participants.add(review['user']['login'])

                        num_comments = pr.get('comments', 0)

                        participants.add(pr['user']['login'])
                        num_participants = len(participants)

                        description_length = len(pr['body']) if pr['body'] else 0

                        pr_data.append({
                            'repo': repo_full_name,
                            'pr_number': pr_number,
                            'num_files': num_files,
                            'additions': additions,
                            'deletions': deletions,
                            'duration_hours': duration.total_seconds() / 3600,
                            'description_length': description_length,
                            'num_comments': num_comments,
                            'num_reviews': num_reviews,
                            'num_participants': num_participants
                        })
                        
                        total_pr_count += 1
                        print(f'{repo_full_name}: {total_pr_count}')
                    else:
                        print(f'Erro ao obter revisões do PR #{pr_number} em {repo_full_name}: {reviews_response.status_code}')
                    time.sleep(0.5)

        page += 1
        time.sleep(1)
        
        if total_pr_count >= 100:
            break

    return pr_data



def save_repo_data(repo_full_name, pr_data):
    if pr_data:
        repo_csv_filename = f'results/{repo_full_name.replace("/", "_")}_pr_data.csv'
        os.makedirs('results', exist_ok=True)
        df = pd.DataFrame(pr_data)
        df.to_csv(repo_csv_filename, index=False)
        print(f'Dados salvos em {repo_csv_filename}')
    else:
        print(f'Nenhum PR coletado para {repo_full_name}.')

def main():
    repos_csv_path = 'selected_repos.csv'
    
    selected_repos = []
    try:
        with open(repos_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)
            selected_repos = [row[0] for row in reader]
    except FileNotFoundError:
        print(f'Arquivo {repos_csv_path} não encontrado. Verifique o caminho e tente novamente.')
        return

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for repo_full_name in selected_repos:
            futures.append(executor.submit(lambda repo: save_repo_data(repo, collect_pr_metrics(repo)), repo_full_name))

        for future in futures:
            future.result() 
if __name__ == '__main__':
    main()
