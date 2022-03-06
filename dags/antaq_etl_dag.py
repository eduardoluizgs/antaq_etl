# -*- coding: utf-8 -*-

import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable as AirflowVariables

from airflow.utils.dates import days_ago
from airflow.utils.trigger_rule import TriggerRule

from tools.helpers import check_variables, check_connections
from tools.const.connections import Connections
from tools.const.variabels import Variables
from tools.operators.dummy_operator import get_task_dummy_operator

from tasks.captura_dados_por_ano_tarefa import get_grupo_captura_dados_anuario_por_ano
from tasks.extrai_dados_por_ano_tarefa import get_grupo_extrai_dados_anuario_por_ano
from tasks.transforma_dados_grupo import get_grupo_transforma_dados_atracacao_por_ano

# *******************************************
#
# DAG Configuration/Context
#
# *******************************************

DAG_ID='antaq_etl'

ENV = 'development' # os.getenv('AIRFLOW_ENV')
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

check_variables(Variables.all())
# check_connections(Connections.all()) # TODO : Review this

context = dict(
    schedule_interval=AirflowVariables.get(Variables.ANTAQ_ETL_DAG_SCHEDULE_INTERVAL),
    data_path=os.path.join(BASE_PATH, 'data'),
    storage_path=os.path.join(
        BASE_PATH,
        'storage',
        DAG_ID,
        '{{ ts_nodash }}_{{ %s }}' % (
            '0' if ENV == 'development' else 'task_instance.run_id'
        )
    ),
    connection_name=Connections.SQLSERVER_CONN_ID,
    env=ENV
)

# *******************************************
#
# DAG Definition
#
# *******************************************

dag = DAG(
    dag_id=DAG_ID,
    description='Extracao e Transformacao de dados para do Anuário Estatísticos da ANTAQ (Agência Nacional de Transportes Aquáticos)',
    schedule_interval=None if context.get('schedule_interval') == 'None' else context.get('schedule_interval'),
    start_date=datetime.now(),
    # start_date=days_ago(1),
    catchup=False,
    default_args=dict(
        # email=['desenvolvimento@avanceig.com.br'],
        # email_on_failure=True,
        # email_on_retry=True,
        retries=5,
        retry_delay=timedelta(minutes=5),
        depends_on_past=True
    )
)
context.update({'dag': dag})

# *******************************************
#
# Task's Definition
#
# *******************************************

grupo_inicio = get_task_dummy_operator('grupo_inicio', **context)
grupo_captura = get_task_dummy_operator('grupo_captura', **context)
grupo_extracao = get_task_dummy_operator('grupo_extracao', **context)
grupo_transformacao_e_gravacao = get_task_dummy_operator('grupo_transformacao_e_gravacao', **context)
grupo_transformacao_atracacao = get_task_dummy_operator('grupo_transformacao_atracacao', **context)
grupo_notifica_conclusao_processo = get_task_dummy_operator('grupo_notifica_conclusao_processo', **context)
grupo_fim = get_task_dummy_operator('grupo_fim', **context)

get_grupo_captura_dados_anuario_por_ano(grupo_captura, grupo_extracao, **context)
get_grupo_extrai_dados_anuario_por_ano(grupo_extracao, grupo_transformacao_e_gravacao, **context)
get_grupo_transforma_dados_atracacao_por_ano(grupo_transformacao_atracacao, grupo_notifica_conclusao_processo, **context)

# *******************************************
#
# DAG Flow
#
# *******************************************

grupo_inicio >> grupo_captura
# grupo_captura >> grupo_captura_dados_anuario_por_ano
# grupo_captura_dados_anuario_por_ano >> grupo_extracao
# grupo_extracao >> grupo_extrai_dados_anuario_por_ano
# grupo_extrai_dados_anuario_por_ano >> grupo_transformacao_e_gravacao
grupo_transformacao_e_gravacao >> grupo_transformacao_atracacao
# grupo_transformacao_atracacao >> grupo_transforma_dados_atracacao_por_ano
# get_grupo_transforma_dados_atracacao_por_ano >> grupo_notifica_conclusao_processo
grupo_notifica_conclusao_processo >> grupo_fim
