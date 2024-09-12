import requests
import subprocess
import os
import shutil
import csv

TOKEN = "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"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
QUERY = """
query($cursor: String) {
  search(query: "stars:>10000 language:Java", type: REPOSITORY, first: 20, after: $cursor) {
    edges {
      node {
        ... on Repository {
          name
          url
        }
      }
    }
    pageInfo {
      endCursor
      hasNextPage
    }
  }
}
"""

REPO_PRE_DEFINIDO = {
    "nome": "iluwatar/java-design-patterns",
    "url": "https://github.com/iluwatar/java-design-patterns"
}

def run_query(query, variables):
    response = requests.post(
        "https://api.github.com/graphql",
        json={"query": query, "variables": variables},
        headers=HEADERS
    )
    if response.status_code != 200:
        raise Exception(f"Query falhou com status code {response.status_code}. {response.text}")
    return response.json()

def coletar_repositorios():
    repositorios = []
    cursor = None

    while len(repositorios) < 1000:
        result = run_query(QUERY, {'cursor': cursor})
        edges = result["data"]["search"]["edges"]

        for edge in edges:
            repo = edge["node"]
            repositorios.append({
                "nome": repo["name"],
                "url": repo["url"],
            })

        cursor = result["data"]["search"]["pageInfo"]["endCursor"]
    
    return repositorios

def clonar_repositorio(url):
    nome_repositorio = url.split("/")[-1]
    caminho = os.path.join("repositorios", nome_repositorio)

    if os.path.exists(caminho):
        print(f"Diretório {caminho} já existe. Limpando o diretório.")
        shutil.rmtree(caminho)  # Remove o diretório existente

    subprocess.run(["git", "clone", url, caminho], check=True)
    return caminho

def executar_ck(caminho_repositorio):
    ck_jar = "ck-0.7.0-jar-with-dependencies.jar"
    resultado = subprocess.run(["java", "-jar", ck_jar, caminho_repositorio], capture_output=True, text=True)
    if "Metrics extracted!!!" in resultado.stdout:
        print("Métricas coletadas com sucesso!")
    else:
        print("Falha ao coletar métricas.")

def main():
    print("Coletando os 1.000 repositórios Java mais populares...")
    repositorios = coletar_repositorios()
    
    for repo in repositorios:
        print(f"Nome: {repo['nome']}, URL: {repo['url']}")

    # Usar o repositório pré-definido para clonar e calcular métricas
    print(f"\nClonando o repositório pré-definido: {REPO_PRE_DEFINIDO['nome']}...")
    caminho_repositorio = clonar_repositorio(REPO_PRE_DEFINIDO["url"])
    print("Executando CK no repositório pré-definido...")
    executar_ck(caminho_repositorio)

if __name__ == "__main__":
    main()

