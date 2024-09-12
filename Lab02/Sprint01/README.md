# Lab02S01 - Análise de Repositórios Java Populares

## Visão Geral

Este projeto faz parte do Lab02S01 e tem como objetivo listar 1.000 repositórios Java populares no GitHub, clonar um repositório pré-definido que contenha arquivos Java com métodos e, em seguida, coletar métricas de código usando a ferramenta CK (Chidamber and Kemerer Java Metrics Tool).

## Arquivos Gerados

Após a execução do script `lab02s01.py`, são gerados os seguintes arquivos:

- **`class.csv`**: Contém métricas no nível de classe do código Java. As métricas incluem acoplamento (CBO), profundidade da herança (DIT), complexidade ciclomática (WMC), falta de coesão (LCOM), número de métodos (NOM), entre outras.
  
- **`method.csv`**: Contém métricas no nível de método para cada classe Java analisada, incluindo complexidade ciclomática, quantidade de loops, declarações de retorno, e outras métricas relevantes.

## Execução do Script

O script `lab02s01.py` realiza as seguintes etapas:

1. **Listagem dos Repositórios**: Utiliza a API GraphQL do GitHub para listar os 1.000 repositórios Java mais populares. A listagem é exibida no terminal.

2. **Clonagem do Repositório**: O script clona um repositório pré-definido que foi escolhido previamente para garantir que contenha arquivos Java com métodos, permitindo a análise adequada com a ferramenta CK.

3. **Coleta de Métricas**: Utiliza a ferramenta CK para analisar o código Java do repositório clonado e gerar os arquivos `class.csv` e `method.csv` contendo as métricas de qualidade de código.

## Observações

- O repositório clonado para análise foi o `iluwatar/java-design-patterns`, previamente selecionado, garantindo que ele contenha os arquivos `.java` necessários para a coleta de métricas.
- A ferramenta CK deve estar presente na pasta raiz do projeto como `ck-0.7.0-jar-with-dependencies.jar`.
- Certifique-se de ter o Java configurado corretamente no seu sistema para executar o CK sem problemas.

## Como Executar

Para executar o script, basta rodar o seguinte comando no terminal:

```bash
python lab02s01.py
