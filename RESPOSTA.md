# Guia de Respostas

## 1) Auto avaliação

Auto-avalie suas habilidades nos requisitos de acordo com os níveis especificados usando o
link abaixo.

Qual o seu nível de domínio nas técnicas/ferramentas listadas abaixo, onde:
- 0, 1, 2 - não tem conhecimento e experiência;
- 3, 4 ,5 - conhece a técnica e tem pouca experiência;
- 6 - domina a técnica e já desenvolveu vários projetos utilizando-a.

Tópicos de Conhecimento:
- Manipulação e tratamento de dados com Python: **`6`**
- Manipulação e tratamento de dados com Pyspark: **`6`**
- Desenvolvimento de data workflows em Ambiente Azure com databricks: **`3`**
- Desenvolvimento de data workflows com Airflow: **`6`**
- Manipulação de bases de dados NoSQL: **`6`**
- Web crawling e web scraping para mineração de dados: **`6`**
- Construção de APIs: REST, SOAP e Microservices: **`6`**

## 2a) Olhando para todos os dados disponíveis na fonte citada acima, em qual estrutura de banco de dados você orienta guardá-los no nosso Data Lake? SQL ou NoSQL?

Com base na estrutura dos dados atuais, recomendo armazenar em um banco de dados relacional (SQL), uma vez que o esquema de dados para ambos os arquivos está bem definido e possívelmente não passará por mudanças constantes. Apesar de alguns arquivos possuírem um volume de dados considerável, não vejo um aumento neste volume de forma exponencial. Assim, a princípio não vejo escalabilidade como requisito não-funcional para este cenário, o que justificaria a adoção de um banco NoSQL.

## 2b) Scripts de extração e transformação

**Item**                                    |**Localização**
|-----                                      |-----
Scripts de Captura                          |dags/tasks/captura_dados_por_ano_tarefa.py
Scripts de Extração                         |dags/tasks/extrai_dados_por_ano_tarefa.py
Scripts de Transformação                    |dags/tasks/transforma_dados_*_por_ano_tarefa.py
Scripts de Criação da Estrutura de Tabelas  |init-database.sql
Diagrama da estrutura das tabelas           |img/der.png
Configuração da Carga                       |dags/tools/const/variabels.py
Lógica para cargas conteinerizadas          |dags/tasks/transforma_dados_carga_por_ano_tarefa.py : Linha 169

**OBS**: _Os scripts de `captura`, `extração`, `transformação` e `gravação` foram feitos diretamente no `Airflow` utilizando o `PySpark`._

### Diagrama da estrutura final de banco de dados

![antaq-etl-der](img/der.png)

## 2c) Consulta para geração de planilha em excel

**Item**                                    |**Localização**
|-----                                      |-----
Scripts da Query                            |query-atracacoes.sql
Lógica para coluna bônus                    |query-atracacoes.sql : Linha 102 e 115

## 3) Criação de ambiente de desenvolvimento com Linux e Docker.

**Item**                                    |**Localização**
|-----                                      |-----
Arquivo da DAG                              |dags/antaq_etl_dag.py
Criação de tarefas da DAG                   |dags/tasks/processa_dados_grupo.py
Arquivo do imagem do Docker p/ SQL Server   |Dockerfile
Arquivo de aplicações do Docker             |docker-compose.yaml

### Diagrama da estrutura final da DAG

![antaq-etl-dag-view](img/antaq-etl-dag-view.png)

## 4) Configuração de pipelines de CI/CD com Gitlab ou Github

A configuração da pipeline está no arquivo `.gitlab-ci.yml`.

## 5) Implantação de aplicações com Kubernetes

A configuração do cluster kubernetes está nos arquivos:

**Item**                                    |**Localização**
|-----                                      |-----
Arquivo de Deploy do nó Master              |kubernetes/deploy-master.sh
Arquivo de Deploy do nó Filho               |kubernetes/deploy-slave.sh
Arquivo de Deploy do Airflow                |kuberneetes/heml/airflow
