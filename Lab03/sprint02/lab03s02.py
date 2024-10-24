import requests
import time
import csv
from datetime import datetime, timedelta
import pandas as pd

GITHUB_TOKEN = ('GITHUB_TOKEN')
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def collect_pr_metrics(repo_full_name):
    pr_data = []
    page = 1
    per_page = 30
    while True:
        url = f'https://api.github.com/repos/{repo_full_name}/pulls'
        params = {
            'state': 'closed',
            'sort': 'created',
            'direction': 'desc',
            'per_page': per_page,
            'page': page
        }
        response = requests.get(url, headers=HEADERS, params=params)
        if response.status_code != 200:
            print(f'Erro ao obter PRs de {repo_full_name}: {response.status_code}')
            break
        prs = response.json()
        if not prs:
            break
        for pr in prs:
            if pr['merged_at'] or pr['state'] == 'closed':
                pr_number = pr['number']
                pr_created_at = datetime.strptime(pr['created_at'], '%Y-%m-%dT%H:%M:%SZ')
                pr_closed_at_str = pr['closed_at'] if pr['closed_at'] else pr['merged_at']
                pr_closed_at = datetime.strptime(pr_closed_at_str, '%Y-%m-%dT%H:%M:%SZ')
                duration = pr_closed_at - pr_created_at
                if duration >= timedelta(hours=1):
                    reviews_url = pr['url'] + '/reviews'
                    reviews_response = requests.get(reviews_url, headers=HEADERS)
                    if reviews_response.status_code == 200:
                        reviews = reviews_response.json()
                        if len(reviews) >= 1:
                            files_url = pr['url'] + '/files'
                            files_response = requests.get(files_url, headers=HEADERS)
                            files = files_response.json()
                            num_files = len(files)
                            additions = sum([file.get('additions', 0) for file in files])
                            deletions = sum([file.get('deletions', 0) for file in files])
                            description_length = len(pr['body']) if pr['body'] else 0
                            comments_url = pr['comments_url']
                            comments_response = requests.get(comments_url, headers=HEADERS)
                            comments = comments_response.json()
                            num_comments = len(comments)
                            participants = set()
                            for comment in comments:
                                participants.add(comment['user']['login'])
                            for review in reviews:
                                participants.add(review['user']['login'])
                            num_participants = len(participants)
                            pr_data.append({
                                'repo': repo_full_name,
                                'pr_number': pr_number,
                                'num_files': num_files,
                                'additions': additions,
                                'deletions': deletions,
                                'duration_hours': duration.total_seconds() / 3600,
                                'description_length': description_length,
                                'num_comments': num_comments,
                                'num_participants': num_participants
                            })
                    else:
                        print(f'Erro ao obter revisões do PR #{pr_number} em {repo_full_name}: {reviews_response.status_code}')
                    time.sleep(0.5)
        page += 1
        time.sleep(1)
    return pr_data

def main():
    # Ajustando o caminho para o arquivo 'selected_repos.csv'
    repos_csv_path = 'selected_repos.csv'
    
    selected_repos = []
    try:
        with open(repos_csv_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            next(reader)  # Ignora o cabeçalho
            selected_repos = [row[0] for row in reader]
    except FileNotFoundError:
        print(f'Arquivo {repos_csv_path} não encontrado. Verifique o caminho e tente novamente.')
        return

    all_pr_data = []
    for repo_full_name in selected_repos:
        print(f'Coletando PRs do repositório {repo_full_name}...')
        pr_data = collect_pr_metrics(repo_full_name)
        if pr_data:
            all_pr_data.extend(pr_data)
            print(f'Total de PRs coletados até agora: {len(all_pr_data)}')
        else:
            print(f'Nenhum PR coletado para {repo_full_name}.')
        time.sleep(2)

    if all_pr_data:
        df = pd.DataFrame(all_pr_data)
        df.to_csv('github_pr_dataset.csv', index=False)
        print('Coleta concluída. Dados completos salvos em github_pr_dataset.csv.')
    else:
        print('Nenhum dado coletado. Verifique os critérios e tente novamente.')

if __name__ == '__main__':
    main()
