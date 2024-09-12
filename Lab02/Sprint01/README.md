# Lab02S01

## Arquivos Gerados

Após a execução do script `lab02s01.py`, são gerados os seguintes arquivos:

- **`class.csv`**: Contém métricas no nível de classe do código Java. As métricas incluem acoplamento (CBO), profundidade da herança (DIT), complexidade ciclomática (WMC), falta de coesão (LCOM), número de métodos (NOM), entre outras.
  
- **`method.csv`**: Contém métricas no nível de método para cada classe Java analisada, incluindo complexidade ciclomática, quantidade de loops, declarações de retorno, e outras métricas relevantes.

- **`field.csv`**: Este arquivo contém informações sobre os campos (variáveis de instância) presentes nas classes do repositório analisado. As colunas incluem o caminho do arquivo, o nome da classe, o método em que o campo está sendo utilizado, o nome do campo e o tipo de uso (como leitura ou escrita). Esse arquivo é útil para entender como e onde os campos das classes são utilizados em diferentes métodos.

- **`variable.csv`**: Este arquivo lista as variáveis locais usadas nos métodos das classes. As colunas incluem o caminho do arquivo, o nome da classe, o método onde a variável é utilizada, e o nome da variável. Esse arquivo permite uma análise detalhada do uso de variáveis locais em cada método, facilitando a análise de complexidade e boas práticas de codificação.

## Execução do Script

O script `lab02s01.py` realiza as seguintes etapas:

1. **Listagem dos Repositórios**: Utiliza a API GraphQL do GitHub para listar os 1.000 repositórios Java mais populares. A listagem é exibida no terminal.

2. **Clonagem do Repositório**: O script clona um repositório pré-definido que foi escolhido previamente para garantir que contenha arquivos Java com métodos, permitindo a análise adequada com a ferramenta CK.

3. **Coleta de Métricas**: Utiliza a ferramenta CK para analisar o código Java do repositório clonado e gerar os arquivos `class.csv` e `method.csv` contendo as métricas de qualidade de código.

## Observações

- O repositório clonado para análise foi o `iluwatar/java-design-patterns`, previamente selecionado, garantindo que ele contenha os arquivos `.java` necessários para a coleta de métricas.
