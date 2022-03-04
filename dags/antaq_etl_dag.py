# -*- coding: utf-8 -*-

import os

from datetime import datetime, timedelta

from airflow import DAG
from airflow.models import Variable

from airflow.utils.trigger_rule import TriggerRule

from tools.operators.dummy_operator import get_task_dummy_operator

from tools.helpers import check_variables, check_connections
from tools.connections import Connections


# *******************************************
#
# DAG Configuration/Context
#
# *******************************************

DAG_ID='antaq_etl'

ENV = os.getenv('AIRFLOW_ENV')
BASE_PATH = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

DAG_VARIABLES =  {
    'antaq_etl_dag_schedule_interval': '0 12 * * *'
}
check_variables(DAG_VARIABLES)

check_connections(Connections.all())

context = dict(
    schedule_interval=Variable.get('antaq_etl_dag_schedule_interval'),
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
    start_date=datetime(2019, 6, 1),
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

# aqui deve entrar uma logica para varrer as pastas dos anos e montar as tarefas de extração
grupo_extracao = get_task_dummy_operator('grupo_extracao', **context)

grupo_transformacao = get_task_dummy_operator('grupo_transformacao', **context)

# tarefa_leitura_dados_ = get_tarefa_captura_tokens_revendedor_gera(**context)

grupo_fim = get_task_dummy_operator('grupo_fim', **context)

# *******************************************
#
# DAG Flow
#
# *******************************************

grupo_inicio >> grupo_extracao

grupo_extracao >> grupo_transformacao

grupo_transformacao >> grupo_fim
