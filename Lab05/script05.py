import requests
import time
import json
import pandas as pd

# URLs e Token de Autenticação
GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"
TOKEN = "token"  # Substitua pelo seu token do GitHub

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

# Número total de itens desejados e itens por página
TOTAL_ITEMS = 100
ITEMS_PER_PAGE = 20  # Definimos um valor menor para controlar a paginação

# Consultas GraphQL com Paginação
# Consulta Simples
def get_graphql_query_simple(after_cursor=None):
    after_clause = f', after: "{after_cursor}"' if after_cursor else ''
    return f'''
    query {{
      search(query: "stars:>100", type: REPOSITORY, first: {ITEMS_PER_PAGE}{after_clause}) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        edges {{
          node {{
            ... on Repository {{
              name
              description
            }}
          }}
        }}
      }}
    }}
    '''

# Consulta Complexa
def get_graphql_query_complex(after_cursor=None):
    after_clause = f', after: "{after_cursor}"' if after_cursor else ''
    return f'''
    query {{
      search(query: "stars:>100", type: REPOSITORY, first: {ITEMS_PER_PAGE}{after_clause}) {{
        pageInfo {{
          endCursor
          hasNextPage
        }}
        edges {{
          node {{
            ... on Repository {{
              name
              description
              stargazerCount
              forkCount
              primaryLanguage {{
                name
              }}
              owner {{
                login
                url
              }}
              issues(first: 5) {{
                totalCount
                edges {{
                  node {{
                    title
                    number
                    createdAt
                  }}
                }}
              }}
            }}
          }}
        }}
      }}
    }}
    '''

# Parâmetros REST com Paginação
REST_ENDPOINT = "/search/repositories"
REST_PARAMS_SIMPLE = {"q": "stars:>100", "per_page": ITEMS_PER_PAGE}

def measure_graphql(query_func):
    total_response_time = 0
    total_response_size = 0
    status_code = 200
    items_retrieved = 0
    has_next_page = True
    after_cursor = None

    while has_next_page and items_retrieved < TOTAL_ITEMS:
        query = query_func(after_cursor)
        start_time = time.time()
        try:
            response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": query})
            end_time = time.time()
            response_time = end_time - start_time
            response_size = len(response.content)
            status_code = response.status_code

            if status_code != 200:
                print(f"GraphQL request failed with status code {status_code}")
                return total_response_time, total_response_size, status_code, None

            data = response.json()
            total_response_time += response_time
            total_response_size += response_size

            # Atualizar o cursor e verificar se há próxima página
            page_info = data['data']['search']['pageInfo']
            has_next_page = page_info['hasNextPage']
            after_cursor = page_info['endCursor']
            items_retrieved += len(data['data']['search']['edges'])

            # Respeitar os limites de taxa
            check_rate_limit(response.headers)
            time.sleep(1)  # Pequeno atraso para evitar excesso de requisições

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"GraphQL request exception: {e}")
            return total_response_time, total_response_size, None, None

    return total_response_time, total_response_size, status_code, None

def measure_rest(params, complex_query=False):
    total_response_time = 0
    total_response_size = 0
    status_codes = []
    items_retrieved = 0
    page = 1

    while items_retrieved < TOTAL_ITEMS:
        params['page'] = page
        start_time = time.time()
        try:
            response = requests.get(REST_URL + REST_ENDPOINT, headers=HEADERS, params=params)
            end_time = time.time()
            response_time = end_time - start_time
            response_size = len(response.content)
            status_code = response.status_code
            status_codes.append(status_code)

            if status_code != 200:
                print(f"REST request failed with status code {status_code}")
                return total_response_time, total_response_size, status_codes, None

            data = response.json()
            items = data.get('items', [])
            items_retrieved += len(items)
            total_response_time += response_time
            total_response_size += response_size

            # Respeitar os limites de taxa
            check_rate_limit(response.headers)
            time.sleep(1)  # Pequeno atraso para evitar excesso de requisições

            if complex_query:
                # Requisições adicionais para dados complexos
                for repo in items:
                    # Obter detalhes do proprietário
                    owner_url = repo['owner']['url']
                    owner_response = requests.get(owner_url, headers=HEADERS)
                    total_response_time += owner_response.elapsed.total_seconds()
                    total_response_size += len(owner_response.content)
                    status_code = owner_response.status_code
                    status_codes.append(status_code)

                    if status_code != 200:
                        print(f"REST owner request failed with status code {status_code}")
                        continue

                    # Obter issues (primeiras 5)
                    issues_url = repo['issues_url'].replace('{/number}', '')
                    issues_params = {'per_page': 5}
                    issues_response = requests.get(issues_url, headers=HEADERS, params=issues_params)
                    total_response_time += issues_response.elapsed.total_seconds()
                    total_response_size += len(issues_response.content)
                    status_code = issues_response.status_code
                    status_codes.append(status_code)

                    if status_code != 200:
                        print(f"REST issues request failed with status code {status_code}")
                        continue

                    # Respeitar os limites de taxa
                    check_rate_limit(owner_response.headers)
                    check_rate_limit(issues_response.headers)
                    time.sleep(0.5)

            page += 1

        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            print(f"REST request exception: {e}")
            return total_response_time, total_response_size, status_codes, None

    return total_response_time, total_response_size, status_codes, None

def check_rate_limit(headers):
    remaining = int(headers.get('X-RateLimit-Remaining', 1))
    reset_time = int(headers.get('X-RateLimit-Reset', time.time()))
    if remaining == 0:
        sleep_time = max(reset_time - time.time(), 0)
        print(f"Rate limit reached. Sleeping for {sleep_time} seconds.")
        time.sleep(sleep_time)

def run_experiment():
    results = []
    for i in range(10):  # 10 medições
        print(f"Iniciando iteração {i + 1}")

        # Consulta Simples
        graphql_time, graphql_size, graphql_status, _ = measure_graphql(get_graphql_query_simple)
        rest_time, rest_size, rest_statuses, _ = measure_rest(REST_PARAMS_SIMPLE.copy(), complex_query=False)

        results.append({
            "Iteration": i + 1,
            "Method": "GraphQL",
            "QueryType": "Simple",
            "ResponseTime": graphql_time,
            "ResponseSize": graphql_size,
            "StatusCode": graphql_status
        })
        rest_overall_status = max(rest_statuses) if rest_statuses else None
        results.append({
            "Iteration": i + 1,
            "Method": "REST",
            "QueryType": "Simple",
            "ResponseTime": rest_time,
            "ResponseSize": rest_size,
            "StatusCode": rest_overall_status
        })

        # Consulta Complexa
        graphql_time, graphql_size, graphql_status, _ = measure_graphql(get_graphql_query_complex)
        rest_time, rest_size, rest_statuses, _ = measure_rest(REST_PARAMS_SIMPLE.copy(), complex_query=True)

        rest_overall_status = max(rest_statuses) if rest_statuses else None
        results.append({
            "Iteration": i + 1,
            "Method": "GraphQL",
            "QueryType": "Complex",
            "ResponseTime": graphql_time,
            "ResponseSize": graphql_size,
            "StatusCode": graphql_status
        })
        results.append({
            "Iteration": i + 1,
            "Method": "REST",
            "QueryType": "Complex",
            "ResponseTime": rest_time,
            "ResponseSize": rest_size,
            "StatusCode": rest_overall_status
        })

    df = pd.DataFrame(results)
    df.to_csv("experiment_results_100.csv", index=False)
    print("Resultados salvos em experiment_results_100.csv")

if __name__ == "__main__":
    run_experiment()
