# -*- coding: utf-8 -*-

import os
import json

from zipfile import ZipFile

from airflow.exceptions import AirflowException

from airflow.models import Variable as AirflowVariables
from airflow.operators.python_operator import PythonOperator

from tools.tasks.storage_task import StorageTask

from tools.const.variabels import Variables
from tools.const.tasks import Tasks


class ExtraiDadosAnuario(StorageTask):

    storage_path_captured = None
    storage_path = None
    year = None

    @classmethod
    def _pre_execute(cls, **kwargs):

        super()._pre_execute(**kwargs)

        cls.storage_path = kwargs.get('storage_path', None)
        if not cls.storage_path:
            raise AirflowException('Invalid Storage Path!')

        cls.year = kwargs.get('year', None)
        if not cls.year:
            raise AirflowException('Invalid Year!')

        cls.storage_path = cls.task_instance.task.render_template(
            cls.storage_path,
            cls.task_instance.get_template_context()
        )

        cls.storage_path_captured = os.path.join(cls.storage_path, 'captured')
        cls.storage_path = os.path.join(cls.storage_path, 'extracted', str(cls.year))

    @classmethod
    def _execute(cls, **kwargs):

        file_path = os.path.join(cls.storage_path_captured, '{}.zip'.format(cls.year))
        if not os.path.isfile(file_path):
            raise AirflowException(u'Arquivo de dados para o ano {} não encontrado!'.format(cls.year))

        try:
            with ZipFile(file_path, 'r') as zf:
                zf.extractall(cls.storage_path)
        except:
            raise AirflowException(u'Arquivo de dados para o ano {} está corrompido!'.format(cls.year))

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_extrai_dados_anuario_por_ano(year, **context):
    """ Retorna uma tarefa de extração dos dados do anuário para cada ano configurado.

        NOTE : Eduardo Luiz
        Esta função cria um PythonOperator informando o caminho de armazenamento dos arquivos e o ano.
    """

    return PythonOperator(
            task_id='{}_{}'.format(Tasks.TAREFA_EXTRAI_DADOS_ANUARIO, year),
            python_callable=ExtraiDadosAnuario,
            op_kwargs=dict(
                depends_on=[],
                storage_path=context.get('storage_path'),
                year=year
            ),
            depends_on_past=True,
            provide_context=True,
            dag=context['dag']
        )
