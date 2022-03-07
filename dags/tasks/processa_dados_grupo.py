# -*- coding: utf-8 -*-

import json

from airflow.models import Variable as AirflowVariables

from tools.const.variabels import Variables

from tools.operators.dummy_operator import get_task_dummy_operator

from tasks.captura_dados_por_ano_tarefa import get_tarefa_captura_produtos

from tasks.extrai_dados_por_ano_tarefa import get_tarefa_extrai_dados_anuario_por_ano

from tasks.transforma_dados_atracacao_por_ano_tarefa import get_tarefa_transforma_dados_atracacao_por_ano
from tasks.transforma_dados_carga_por_ano_tarefa import get_tarefa_transforma_dados_carga_por_ano

from tasks.grava_dados_atracacao_por_ano_tarefa import get_tarefa_grava_dados_atracacao_por_ano
from tasks.grava_dados_carga_por_ano_tarefa import get_tarefa_grava_dados_carga_por_ano


def get_grupo_processa_dados_atracacao_por_ano(previous_task, next_task, **context):
    """ Retorna um conjunto de tarefas para processamento dos dados para cada ano configurado."""

    years = json.loads(AirflowVariables.get(Variables.ANTAQ_YEARS_TO_EXTRACT) or [])

    for year in years:

        # cria a tarefa de captura de dados no site da antaq
        captura_task = get_tarefa_captura_produtos(year, **context)

        # NOTE : Eduardo Luiz
        # No futuro deve ser implementando a lógica a tarefa de branch
        # para que o fluxo de execução seja direcionada corretamente
        # por questões práticas de tempo, vamos utilizar apenas um dummy aqui
        branch_task = get_task_dummy_operator(
            'branch_verifica_existencia_dados_anuario_{}'.format(year),
            **context
        )

        # cria a tarefa de notificaçãod e dados inexistentes
        notification_task = get_task_dummy_operator(
            'notifica_nao_existencia_dados_anuario_{}'.format(year),
            **context
        )

        # cria a tarefa de extração de dados
        extrai_task = get_tarefa_extrai_dados_anuario_por_ano(year, **context)

        # cria as tarefas de transformação
        transforma_atracacao_task = get_tarefa_transforma_dados_atracacao_por_ano(year, **context)
        transforma_carga_task = get_tarefa_transforma_dados_carga_por_ano(year, **context)

        # cria as tarefas de gravação de dados
        grava_atracacao_task = get_tarefa_grava_dados_atracacao_por_ano(year, **context)
        grava_carga_task = get_tarefa_grava_dados_carga_por_ano(year, **context)

        # ajusta o fluxo da dag
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
