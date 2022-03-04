# ANTAQ ETL SOLUTION

## Configução do ambiente Docker

Primeiramente crie a imagem do `SQL Server` com assistente de linha de comando, necessário para criação da estrutura inicial da base:

```shell
$ docker build -t sqlserver .
```

Suba o `docker-compose` para iniciar os containers do `SQL Server` e `Airflow`:

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

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Init` na seção `Executar e Depurar (Degug)`.

### Executando a DAG em ambiente local

Após inicialize o banco de dadis do `airflow`:

```shell
$ <project_path>/.venv/bin/python <project_path>/.venv/lib/python3.7/site-packages/airflow dags test antaq_etl YYYY-mm-dd
```

Ou caso esteja utilizando o `VSCode` execute a configuração `Airflow Test Dag` na seção `Executar e Depurar (Degug)`.
