import requests
import time
import csv
from datetime import datetime, timedelta

GITHUB_TOKEN = 'token'
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

def get_top_repositories(n_repos):
    repos = []
    per_page = 100
    pages = n_repos // per_page + (1 if n_repos % per_page > 0 else 0)
    for page in range(1, pages + 1):
        url = f'https://api.github.com/search/repositories?q=stars:>1&sort=stars&order=desc&per_page={per_page}&page={page}'
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            data = response.json()
            repos.extend(data['items'])
            print(f'Repositórios obtidos: {len(repos)}')
        else:
            print(f'Erro ao obter repositórios: {response.status_code}')
            break
        time.sleep(1)  
    return repos[:n_repos]

def has_min_prs(repo_full_name, min_prs=100):
    owner_repo = repo_full_name
    url = 'https://api.github.com/search/issues'
    query = f'repo:{owner_repo} type:pr'
    params = {
        'q': query,
        'per_page': 1
    }
    response = requests.get(url, headers=HEADERS, params=params)
    print(f'Requesting URL: {response.url}')
    if response.status_code == 200:
        data = response.json()
        total_prs = data['total_count']
        print(f'{owner_repo} tem {total_prs} PRs.')
        return total_prs >= min_prs
    else:
        print(f'Erro ao obter PRs de {repo_full_name}: {response.status_code}')
        print(f'Response content: {response.content}')
        return False

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
                            if pr['body']:
                                description_length = len(pr['body'])
                            else:
                                description_length = 0
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
    n_repos = 200
    min_prs = 100
    print('Obtendo os repositórios mais populares...')
    top_repos = get_top_repositories(n_repos)
    print('Filtrando repositórios com pelo menos 100 PRs...')
    selected_repos = []
    for repo in top_repos:
        repo_full_name = repo['full_name']
        print(f'Verificando {repo_full_name}...')
        if has_min_prs(repo_full_name, min_prs):
            print(f'{repo_full_name} selecionado.')
            selected_repos.append(repo_full_name)
        else:
            print(f'{repo_full_name} não possui PRs suficientes.')
        time.sleep(2)
    print(f'Total de repositórios selecionados: {len(selected_repos)}')

    with open('selected_repos.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['repo_full_name'])
        for repo_full_name in selected_repos:
            writer.writerow([repo_full_name])
    print('Lista de repositórios selecionados salva em selected_repos.csv.')

    all_pr_data = []
    for repo_full_name in selected_repos:
        print(f'Coletando PRs do repositório {repo_full_name}...')
        pr_data = collect_pr_metrics(repo_full_name)
        if pr_data:
            all_pr_data.extend(pr_data)
            print(f'Total de PRs coletados até agora: {len(all_pr_data)}')
        else:
            print(f'Nenhum PR coletado para {repo_full_name}.')
        with open('pr_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['repo', 'pr_number', 'num_files', 'additions', 'deletions',
                          'duration_hours', 'description_length', 'num_comments', 'num_participants']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for data in all_pr_data:
                writer.writerow(data)
        time.sleep(2) 

    if all_pr_data:
        print('Coleta concluída. Dados salvos em pr_data.csv.')
    else:
        print('Nenhum dado coletado. Verifique os critérios e tente novamente.')

if __name__ == '__main__':
    main()
