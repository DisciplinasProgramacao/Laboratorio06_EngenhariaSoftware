import requests
import time
import json
import pandas as pd

GRAPHQL_URL = "https://api.github.com/graphql"
REST_URL = "https://api.github.com"
TOKEN = "token" 

HEADERS = {"Authorization": f"Bearer {TOKEN}"}

GRAPHQL_QUERY = """
query {
  search(query: "stars:>100", type: REPOSITORY, first: 10) {
    edges {
      node {
        ... on Repository {
          name
          stargazerCount
          primaryLanguage {
            name
          }
        }
      }
    }
  }
}
"""

REST_ENDPOINT = "/search/repositories"
REST_PARAMS = {"q": "stars:>100", "per_page": 10}

def measure_graphql():
    start_time = time.time()
    response = requests.post(GRAPHQL_URL, headers=HEADERS, json={"query": GRAPHQL_QUERY})
    end_time = time.time()
    response_size = len(response.content)
    response_time = end_time - start_time
    return response_time, response_size, response.json()

def measure_rest():
    start_time = time.time()
    response = requests.get(REST_URL + REST_ENDPOINT, headers=HEADERS, params=REST_PARAMS)
    end_time = time.time()
    response_size = len(response.content)
    response_time = end_time - start_time
    return response_time, response_size, response.json()

def run_experiment():
    results = []
    for i in range(30):  #30 medições
        
        graphql_time, graphql_size, graphql_data = measure_graphql()
        
        rest_time, rest_size, rest_data = measure_rest()
       
        results.append({
            "Iteration": i + 1,
            "Method": "GraphQL",
            "ResponseTime": graphql_time,
            "ResponseSize": graphql_size
        })
        results.append({
            "Iteration": i + 1,
            "Method": "REST",
            "ResponseTime": rest_time,
            "ResponseSize": rest_size
        })

    df = pd.DataFrame(results)
    df.to_csv("experiment_results.csv", index=False)
    print("Resultados salvos em experiment_results.csv")

if __name__ == "__main__":
    run_experiment()