# -*- coding: utf-8 -*-

import json

from airflow.models import Variable as AirflowVariables

from tools.const.variabels import Variables

from tools.operators.dummy_operator import get_task_dummy_operator


def get_grupo_captura_dados_anuario_por_ano(previous_task, next_task, **context):
    """ Retorna um conjunto de tarefas de captura dos dados do anuário para cada ano configurado

        NOTE : Eduardo Luiz
        Estas tarefas são `FAKE` e forão inseridas aqui apenas para montar o gráfico da DAG.
        Os dados utilizados já foram baixados previamente para a pasta `data`do projeto.
    """

    years = json.loads(AirflowVariables.get(Variables.ANTAQ_YEARS_TO_EXTRACT) or [])

    for year in years:

        task_year = get_task_dummy_operator(
            'tarefa_captura_dados_anuario_{}'.format(year),
            **context
        )

        previous_task >> task_year >> next_task
