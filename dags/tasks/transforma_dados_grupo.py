# -*- coding: utf-8 -*-

import json

from airflow.models import Variable as AirflowVariables

from tools.const.variabels import Variables

from tasks.transforma_dados_atracacao_por_ano_tarefa import get_tarefa_transforma_dados_atracacao_por_ano
from tasks.grava_dados_atracacao_por_ano_tarefa import get_tarefa_grava_dados_atracacao_por_ano


def get_grupo_transforma_dados_atracacao_por_ano(previous_task, next_task, **context):
    """ Retorna um conjunto de tarefas de transformação de dados para cada ano configurado."""

    years = json.loads(AirflowVariables.get(Variables.ANTAQ_YEARS_TO_EXTRACT) or [])

    for year in years:

        transforma_atracacao_task = get_tarefa_transforma_dados_atracacao_por_ano(year, **context)
        grava_atracacao_task = get_tarefa_grava_dados_atracacao_por_ano(year, **context)

        previous_task >> \
        transforma_atracacao_task >> \
        grava_atracacao_task >> \
        next_task
