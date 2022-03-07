# -*- coding: utf-8 -*-

import json

from airflow.models import Variable as AirflowVariables

from tools.const.variabels import Variables

from tools.operators.dummy_operator import get_task_dummy_operator

from tasks.extrai_dados_por_ano_tarefa import get_tarefa_extrai_dados_anuario_por_ano

from tasks.transforma_dados_atracacao_por_ano_tarefa import get_tarefa_transforma_dados_atracacao_por_ano
from tasks.transforma_dados_carga_por_ano_tarefa import get_tarefa_transforma_dados_carga_por_ano

from tasks.grava_dados_atracacao_por_ano_tarefa import get_tarefa_grava_dados_atracacao_por_ano
from tasks.grava_dados_carga_por_ano_tarefa import get_tarefa_grava_dados_carga_por_ano


def get_grupo_processa_dados_atracacao_por_ano(previous_task, next_task, **context):
    """ Retorna um conjunto de tarefas de transformação de dados para cada ano configurado."""

    years = json.loads(AirflowVariables.get(Variables.ANTAQ_YEARS_TO_EXTRACT) or [])

    for year in years:

        captura_task = get_task_dummy_operator(
            'tarefa_captura_dados_anuario_{}'.format(year),
            **context
        )

        branch_task = get_task_dummy_operator(
            'branch_verifica_existencia_dados_anuario_{}'.format(year),
            **context
        )

        notification_task = get_task_dummy_operator(
            'notifica_nao_existencia_dados_anuario_{}'.format(year),
            **context
        )

        extrai_task = get_tarefa_extrai_dados_anuario_por_ano(year, **context)

        transforma_atracacao_task = get_tarefa_transforma_dados_atracacao_por_ano(year, **context)
        transforma_carga_task = get_tarefa_transforma_dados_carga_por_ano(year, **context)

        grava_atracacao_task = get_tarefa_grava_dados_atracacao_por_ano(year, **context)
        grava_carga_task = get_tarefa_grava_dados_carga_por_ano(year, **context)

        previous_task >> captura_task
        captura_task >> branch_task
        branch_task >> notification_task
        notification_task >> next_task
        branch_task >> extrai_task
        extrai_task >> [transforma_atracacao_task, transforma_carga_task]
        transforma_atracacao_task >> grava_atracacao_task
        transforma_carga_task >> grava_carga_task
        grava_atracacao_task >> grava_carga_task
        grava_carga_task >> next_task
