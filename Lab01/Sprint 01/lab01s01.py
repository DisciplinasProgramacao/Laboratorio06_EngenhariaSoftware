import requests
import csv
import time
from datetime import datetime
import statistics
import pandas as pd

GITHUB_TOKEN = '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'
HEADERS = {
    'Authorization': f'Bearer {GITHUB_TOKEN}'
}

def create_query(first, cursor=None):
    return '''
    query {
      search(query: "stars:>1", type: REPOSITORY, first: %d, after: %s) {
        pageInfo {
          endCursor
          hasNextPage
        }
        edges {
          node {
            ... on Repository {
              name
              createdAt
              updatedAt
              stargazers {
                totalCount
              }
              primaryLanguage {
                name
              }
              releases {
                totalCount
              }
              pullRequests(states: MERGED) {
                totalCount
              }
              issues {
                totalCount
              }
              closedIssues: issues(states: CLOSED) {
                totalCount
              }
            }
          }
        }
      }
    }
    ''' % (first, f'"{cursor}"' if cursor else "null")

def run_query(query, retries=3):
    for i in range(retries):
        response = requests.post(
            'https://api.github.com/graphql',
            json={'query': query},
            headers=HEADERS
        )
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 504:
            print(f"Timeout. Tentando outra vez... ({i+1}/{retries})")
            time.sleep(2)
        else:
            raise Exception(f"Query falahou: {response.status_code}. {query}")
    
    raise Exception(f"Query falhou depois de {retries} tentativas.")

def collect_data(total_repos=100, batch_size=20):
    cursor = None
    all_repos = []

    while len(all_repos) < total_repos:
        query = create_query(batch_size, cursor)
        result = run_query(query)
        repos = result['data']['search']['edges']
        all_repos.extend(repos)

        cursor = result['data']['search']['pageInfo']['endCursor']
        if not result['data']['search']['pageInfo']['hasNextPage']:
            break

        print(f"{len(all_repos)} repositorios coletados ate agora...")
    
    return all_repos[:total_repos]

def calculate_metrics(repos):
    now = datetime.utcnow()
    
    ages = []
    pull_requests = []
    releases = []
    last_updates = []
    languages = []
    issue_ratios = []
    
    for repo in repos:
        node = repo['node']
        created_at = datetime.strptime(node['createdAt'], "%Y-%m-%dT%H:%M:%SZ")
        updated_at = datetime.strptime(node['updatedAt'], "%Y-%m-%dT%H:%M:%SZ")
        
        # Calcular idade do repositório em anos
        age = (now - created_at).days / 365.25
        ages.append(age)
        
        # Total de pull requests aceitas
        pull_requests.append(node['pullRequests']['totalCount'])
        
        # Total de releases
        releases.append(node['releases']['totalCount'])
        
        # Tempo desde a última atualização em dias
        last_update = (now - updated_at).days
        last_updates.append(last_update)
        
        # Linguagem primária
        language = node['primaryLanguage']['name'] if node['primaryLanguage'] else 'Unknown'
        languages.append(language)
        
        # Razão de issues fechadas
        total_issues = node['issues']['totalCount']
        closed_issues = node['closedIssues']['totalCount']
        issue_ratio = (closed_issues / total_issues) if total_issues > 0 else 0
        issue_ratios.append(issue_ratio)
    
    # Calcular medianas
    median_age = statistics.median(ages)
    median_pull_requests = statistics.median(pull_requests)
    median_releases = statistics.median(releases)
    median_last_update = statistics.median(last_updates)
    median_issue_ratio = statistics.median(issue_ratios)
    
    # Contagem de linguagens
    language_counts = pd.Series(languages).value_counts()

    # Exibir os resultados
    print("\n--- Resultados das Análises ---\n")
    print(f"RQ01: Mediana da idade dos repositórios (anos): {median_age:.2f}")
    print(f"RQ02: Mediana do total de pull requests aceitas: {median_pull_requests}")
    print(f"RQ03: Mediana do total de releases: {median_releases}")
    print(f"RQ04: Mediana do tempo desde a última atualização (dias): {median_last_update}")
    print(f"RQ05: Linguagens mais comuns:\n{language_counts}")
    print(f"RQ06: Mediana da razão de issues fechadas: {median_issue_ratio:.2f}")

def save_to_csv(repos):
    with open('github_repositories_100.csv', 'w', newline='') as csvfile:
        fieldnames = ['name', 'createdAt', 'updatedAt', 'stars', 'language', 'releases', 'pullRequests', 'issues', 'closedIssues']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for repo in repos:
            node = repo['node']
            writer.writerow({
                'name': node['name'],
                'createdAt': node['createdAt'],
                'updatedAt': node['updatedAt'],
                'stars': node['stargazers']['totalCount'],
                'language': node['primaryLanguage']['name'] if node['primaryLanguage'] else 'Unknown',
                'releases': node['releases']['totalCount'],
                'pullRequests': node['pullRequests']['totalCount'],
                'issues': node['issues']['totalCount'],
                'closedIssues': node['closedIssues']['totalCount']
            })

if __name__ == '__main__':
    repos = collect_data(total_repos=100, batch_size=20)
    save_to_csv(repos)
    calculate_metrics(repos)
