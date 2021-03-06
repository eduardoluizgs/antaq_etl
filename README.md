# ANTAQ ETL SOLUTION

Este documento tem como objetivo guiar a instalação e configuração do ambiente do projeto de `ETL` em `Airflow`, para processamento dos dados do `Anuário Estatístico` da `ANTAQ` (`Agência Nacional de Transportes Aquáticos`).

Este projeto foi testado no `Mac OS Monterey 12.1` com Python `3.7`.

## Estrutura da DAG

![antaq-etl-dag-view](img/antaq-etl-dag-view.png)

## Estrutura do Projeto

**Item**            |**Descrição**
|-----              |-----
.vscode/            |Pasta com configurações para execução do projeto no `Visual Studio Code`.
dags/               |Pasta contendo as dags/fluxos de processamento de dados do `Airflow`.
dags/tasks          |Pasta contendo os scripts de `captura`, `extração`, `transformação` e `gravação`.
dags/tools          |Arquivos de helpers e funções genéricas e uso geral.
storage/            |Pasta para armazenar de forma temporário os arquivos de dados.
airflow-artigo.pdf  |Mini artigo sobre `Airflow`.
airflow.cfg         |Arquivo de configuração do `Airflow` para execução em ambiente local.
Dockerfile          |Arquivo de imagem `docker` para criação do container `SQL Server`. Necssário para injeção do utilitário de linha de comando para criação da estrutura inicial do banco de dados.
docker-compose.yml  |Arquivo com configurações para criação de containers do `Airflow`, `Spark`e `SQL Server`.
init-database.sql   |Script SQL para criação da estrutura inicial do banco de dados `SQL Server`.
requirements.txt    |Arquivo contando bibliotecas necessárias para execução do projeto.


## Configução do ambiente Docker

Primeiramente crie a imagem do `SQL Server` com assistente de linha de comando, necessário para criação da estrutura inicial da base:

```shell
$ docker build -t sqlserver .
```

Suba o `docker-compose` para iniciar os containers do `SQL Server`, `Airflow` e `Spark`:

```shell
$ docker-compose up -d
```

## Configução do ambiente local

Caso queria debugar o projeto localmente, crie um novo ambiente virtual:

```shell
$ python3 -m virtualenv --python=python3.7 .venv
```

Em seguida, instale o `airflow` via `pip`:

```shell
$ pip install 'apache-airflow==2.2.4' --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.2.4/constraints-3.7.txt"
 ```

Configure a variável de ambiente do `airflow`:

```shell
export AIRFLOW_HOME=<project_path>
```

Para tornar a variável de ambiente persistente, adicione o comando acima ao arquivo `.bash_profile`.

Ajuste os caminhos no arquivo de configuração `airflow.cfg`:

```
[core]

dags_folder = /<project_path>/dags
plugins_folder = /<project_path>/plugins
sql_alchemy_conn = sqlite:////<project_path>/airflow.db

...

[logging]

base_log_folder = /<project_path>/logs
dag_processor_manager_log_location = /<project_path>/logs/dag_processor_manager/dag_processor_manager.log
child_process_log_directory = /<project_path>/logs/scheduler
```

Caso queira carregar as `dags` de exemplo ajuste a configuração abaixo para `true`:

```
[core]]
load_examples = True
```

Após inicialize o banco de dadis do `airflow`:

```shell
$ <project_path>/.venv/bin/python <project_path>/.venv/lib/python3.7/site-packages/airflow db init
```

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Init DB` na seção `Executar e Depurar (Degug)`.

Após crie o usuário `Admin` do `airflow`:

```shell
<project_path>/.venv/bin/python <project_path>/.venv/lib/python3.7/site-packages/airflow \
    users create \
    --username airflow \
    --firstname Airflow \
    --lastname Admin \
    --role Admin \
    --email admin@airflow.org
```

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Init Admin User` na seção `Executar e Depurar (Degug)`.

Para que sua `dag` não falhe durante o processo de `debug`, ajuste o arquivo de configuração `airflow.cfg`:

```
# How long before timing out a python file import
dagbag_import_timeout = 0
```

A `DAG` atual realiza comunicação com o `Spark`. Para instalar o `Spark` e o `PySpark` execute (`Homebrew` é necessário aqui):

```shell
$ brew install openjdk@11
$ brew install scala (optional)
$ brew install apache-spark
```

Por fim, instale os pacotes adicionais do projeto:

```shell
pip install -r requeriments.txt
```

### Iniciando o Webserver em ambiente local

Para inicializar a interface gráfica do `airflow` execute:

```shell
$ <project_path>/.venv/bin/python <project_path>/.venv/lib/python3.7/site-packages/airflow webserver
```

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Webserver` na seção `Executar e Depurar (Degug)`.

Após o `webserver` ser iniciado, é necessário ajustar a conexão com o `SQL Server`. Acesse a opção `Admin > Connections` na interface gráfica, e edite os dados da conexão `mssql_default`. Também é necessário criar uma conexão para o site da `ANTAQ` com o endereço: `http://web.antaq.gov.br`.

### Executando a DAG em ambiente local

Após inicialize o banco de dados do `airflow`:

```shell
$ <project_path>/.venv/bin/python <project_path>/.venv/lib/python3.7/site-packages/airflow dags test antaq_etl YYYY-mm-dd
```

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Test Dag` na seção `Executar e Depurar (Degug)`.
