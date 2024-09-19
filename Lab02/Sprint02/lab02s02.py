import csv
import json
import traceback
import requests
import subprocess
import os
from datetime import datetime

TOKEN = "ADICIONAR-TOKEN"
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
QUERY = """
query($cursor: String) {
  search(query: "stars:>3000 language:Java", type: REPOSITORY, first: 50, after: $cursor) {
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
        headers=HEADERS,
        timeout=60
    )
    if response.status_code != 200:
        raise Exception(f"Query falhou com status code {response.status_code}. {response.text}")
    return response.json()

def coletar_repositorios():
    repositorios = []
    cursor = None

    while len(repositorios) < 1000:
        result = run_query(QUERY, {'cursor': cursor})

        if 'data' not in result:
            print("Resposta da API não contém 'data':", result)
            break

        edges = result["data"]["search"]["edges"]
        repositorios.extend({
            "nome": edge["node"]["name"],
            "url": edge["node"]["url"],
            "estrelas": edge["node"]["stargazers"]["totalCount"],
            "releases": edge["node"]["releases"]["totalCount"],
            "idade": calcular_idade(edge["node"]["createdAt"])
        } for edge in edges)

        page_info = result["data"]["search"]["pageInfo"]
        if not page_info["hasNextPage"]:
            break

        cursor = page_info["endCursor"]

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
    
    try:
        subprocess.run(["git", "clone", url, caminho], check=True)
        print(f"Repositório {nome_repositorio} clonado com sucesso!")
        return caminho
    except subprocess.CalledProcessError as e:
        mensagem = f"Falha ao clonar o repositório {url}. Erro: {e}"
        print(mensagem)
        log_erro(mensagem, e)
        return None

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
            with open(metrics_file, newline='', encoding='utf-8') as csvfile:
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

def deletar_repositorio():
    caminho_repositorio = "./repositorios"
    if os.path.exists(caminho_repositorio):
        try:
            os.system(f'rmdir /S /Q "{caminho_repositorio}"')
            print(f"{caminho_repositorio} excluído com sucesso.")
        except Exception as e:
            print(f"Erro ao excluir o repositório {caminho_repositorio}: {e}")

def salvar_csv(repo, nome_arquivo="repositorios_metricas.csv"):
    with open(nome_arquivo, mode='a', newline='') as file:
        fieldnames = ["nome", "url", "estrelas", "releases", "idade", "CBO", "DIT", "LCOM", "LOC"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writerow(repo)

def salvar_repositorios(repositorios, arquivo):
    with open(arquivo, 'w') as f:
        json.dump(repositorios, f, indent=4)

def carregar_repositorios(arquivo):
    with open(arquivo, 'r') as f:
        return json.load(f)
    
def log_erro(mensagem, exception=None):
    with open('erros.log', 'a') as log_file:
        log_file.write(mensagem + "\n")
        if exception:
            log_file.write(traceback.format_exc() + "\n")
        log_file.write("\n")

def main():
    arquivo_repositorios = 'repositorios.json'

    if os.path.exists(arquivo_repositorios):
        print("Carregando repositórios do arquivo...")
        repositorios = carregar_repositorios(arquivo_repositorios)
    else:
        print("Coletando repositórios do GitHub...")
        repositorios = coletar_repositorios()
        salvar_repositorios(repositorios, arquivo_repositorios)
    
    for repo in repositorios:
        print(f"Nome: {repo['nome']}, URL: {repo['url']}")
        
        print(f"\nClonando o repositório: {repo['nome']}...")
        caminho_repositorio = clonar_repositorio(repo["url"])
        
        if(caminho_repositorio):
            print("Executando CK no repositório...")
            metricas_ck = executar_ck(caminho_repositorio)
        
        print("Deletando o repositório...")
        deletar_repositorio()

        repo.update(metricas_ck)
        print("Salvando resultados em CSV...")
        salvar_csv(repo)


if __name__ == "__main__":
    main()
