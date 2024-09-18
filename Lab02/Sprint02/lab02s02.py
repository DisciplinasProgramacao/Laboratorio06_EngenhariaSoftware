import csv
import requests
import subprocess
import os
import shutil
from datetime import datetime

TOKEN = "<ADICIONAR-TOKEN>"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
# PASSAR PRA 1000
QUERY = """
query($cursor: String) {
  search(query: "stars:>10000 language:Java", type: REPOSITORY, first: 5, after: $cursor) {
    edges {
      node {
        ... on Repository {
          name
          url
          stargazers {
            totalCount
          }
          releases {
            totalCount
          }
          createdAt
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
    # PASSAR PRA 1000
    while len(repositorios) < 5:
        result = run_query(QUERY, {'cursor': cursor})
        edges = result["data"]["search"]["edges"]

        for edge in edges:
            repo = edge["node"]
            nome = repo["name"]
            url = repo["url"]
            estrelas = repo["stargazers"]["totalCount"]
            releases = repo["releases"]["totalCount"]
            idade = calcular_idade(repo["createdAt"])

            repositorios.append({
                "nome": nome,
                "url": url,
                "estrelas": estrelas,
                "releases": releases,
                "idade": idade
            })

        cursor = result["data"]["search"]["pageInfo"]["endCursor"]

    return repositorios

def calcular_idade(created_at):
    data_criacao = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%SZ")
    hoje = datetime.now()
    return (hoje - data_criacao).days / 365.25

def clonar_repositorio(url):
    nome_repositorio = url.split("/")[-1]
    caminho = os.path.join("repositorios", nome_repositorio)

    if os.path.exists(caminho):
        print(f"Diretório {caminho} já existe.")
        return caminho

    subprocess.run(["git", "clone", url, caminho], check=True)
    return caminho

def executar_ck(caminho_repositorio):
    ck_jar = "../Sprint01/ck-0.7.0-jar-with-dependencies.jar"
    
    resultado = subprocess.run(
       ["java", "-jar", ck_jar, caminho_repositorio], 
        capture_output=True, text=True
    )
    print("Output do CK:", resultado.stdout)
    print("Erros do CK:", resultado.stderr)
    
    if "Metrics extracted!!!" in resultado.stdout:
        print("Métricas coletadas com sucesso!")
        
        metrics_file = "class.csv"
        
        try:
            with open(metrics_file, newline='') as csvfile:
                reader = csv.DictReader(csvfile)

                total_cbo = 0
                total_dit = 0
                total_lcom = 0
                loc = 0
                num_classes = 0

                for row in reader:
                    cbo = int(row['cbo'])
                    dit = int(row['dit'])
                    lcom = int(row['lcom'])
                    loc += int(row['loc'])

                    total_cbo += cbo
                    total_dit += dit
                    total_lcom += lcom
                    num_classes += 1
                
                if num_classes > 0:
                    avg_cbo = total_cbo / num_classes
                    avg_dit = total_dit / num_classes
                    avg_lcom = total_lcom / num_classes
                else:
                    avg_cbo, avg_dit, avg_lcom = None, None, None

                return {"CBO": avg_cbo, "DIT": avg_dit, "LCOM": avg_lcom, "LOC": loc}
        
        except FileNotFoundError as e:
            print(f"Erro ao abrir o arquivo CSV: {e}")
            return {"CBO": None, "DIT": None, "LCOM": None, "LOC": None}
    else:
        print("Falha ao coletar métricas.")
        return {"CBO": None, "DIT": None, "LCOM": None, "LOC": None}

def deletar_repositorio(caminho_repositorio):
    if os.path.exists(caminho_repositorio):
        try:
            shutil.rmtree(caminho_repositorio)
            print(f"Repositório {caminho_repositorio} excluído com sucesso.")
        except PermissionError as e:
            print(f"Permissão negada ao excluir {caminho_repositorio}: {e}")
        except Exception as e:
            print(f"Erro ao excluir o repositório {caminho_repositorio}: {e}")

def salvar_csv(repositorios, nome_arquivo="repositorios_metricas.csv"):
    with open(nome_arquivo, mode='w', newline='') as file:
        fieldnames = ["nome", "url", "estrelas", "releases", "idade", "CBO", "DIT", "LCOM", "LOC"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()

        for repo in repositorios:
            writer.writerow(repo)

def main():
    print("Coletando os 1.000 repositórios Java mais populares...")
    repositorios = coletar_repositorios()
    
    resultados = []
    
    for repo in repositorios:
        print(f"Nome: {repo['nome']}, URL: {repo['url']}")
        
        print(f"\nClonando o repositório: {repo['nome']}...")
        caminho_repositorio = clonar_repositorio(repo["url"])
        
        print("Executando CK no repositório...")
        metricas_ck = executar_ck(caminho_repositorio)
        
        print("Deletando o repositório...")
        deletar_repositorio(caminho_repositorio)

        repo.update(metricas_ck)

        resultados.append(repo)
    
    print("Salvando resultados em CSV...")
    salvar_csv(resultados)

if __name__ == "__main__":
    main()
