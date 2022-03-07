# -*- coding: utf-8 -*-

import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable as AirflowVariables

from tools.helpers import check_variables, check_connections
from tools.const.connections import Connections
from tools.const.variabels import Variables
from tools.operators.dummy_operator import get_task_dummy_operator

from tasks.processa_dados_grupo import get_grupo_processa_dados_atracacao_por_ano


# *******************************************
#
# DAG Configuration/Context
#
# *******************************************

DAG_ID='antaq_etl'
DAG_DESCRIPTION='Extracao e Transformacao de dados para do Anuário Estatísticos da ANTAQ (Agência Nacional de Transportes Aquáticos)'
ENV = os.getenv('AIRFLOW_ENV') or 'development'
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

context = dict(
    storage_path=os.path.join(
        BASE_PATH,
        'storage',
        DAG_ID,
        '{{ ts_nodash }}_{{ %s }}' % (
            '0' if ENV == 'development' else 'task_instance.run_id'
        )
    ),
    env=ENV
)

# cria as variaveis e conexoes necessárias para esta DAG
# necessário para evitar erros na leitura inicial da DAG
check_variables(Variables.all())
# check_connections(Connections.all())

# *******************************************
#
# DAG Definition
#
# *******************************************

dag = DAG(
    dag_id=DAG_ID,
    description=DAG_DESCRIPTION,
    schedule_interval=AirflowVariables.get(Variables.ANTAQ_ETL_DAG_SCHEDULE_INTERVAL),
    start_date=datetime(2022, 3, 6),
    catchup=False,
    default_args=dict(
        email=['email@airflow.com.br'],
        email_on_failure=True,
        email_on_retry=False,
        retries=5,
        retry_delay=timedelta(minutes=5),
        depends_on_past=False
    )
)
context.update({'dag': dag})

# *******************************************
#
# Task's Definition
#
# *******************************************

grupo_inicio = get_task_dummy_operator('grupo_inicio', **context)
grupo_processamento = get_task_dummy_operator('grupo_processamento', **context)
grupo_notifica_conclusao_processo = get_task_dummy_operator('grupo_notifica_conclusao_processo', **context)
grupo_fim = get_task_dummy_operator('grupo_fim', **context)

get_grupo_processa_dados_atracacao_por_ano(grupo_processamento, grupo_notifica_conclusao_processo, **context)

# *******************************************
#
# DAG Flow
#
# *******************************************

grupo_inicio >> grupo_processamento
# verificar o fluxo em get_grupo_processa_dados_atracacao_por_ano()
grupo_notifica_conclusao_processo >> grupo_fim
