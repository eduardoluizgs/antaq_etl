# -*- coding: utf-8 -*-

import os

from airflow.exceptions import AirflowException

from requests.models import Response

from tools.operators.http_operator import SimpleHttpOperator

from tools.const.tasks import Tasks
from tools.tasks.abstract_task import AbstractTask

from tools.const.connections import Connections



class CheckResponseTask(AbstractTask):

    content = None
    storage_path = None
    year = None

    @classmethod
    def _pre_execute(cls, **kwargs):

        super()._pre_execute(**kwargs)

        cls.year = kwargs.get('year', None)
        if not cls.year:
            raise AirflowException('Invalid Year!')

        cls.storage_path = kwargs.get('storage_path', None)
        if not cls.storage_path:
            raise AirflowException('Invalid Storage Path!')

        cls.storage_path = cls.task_instance.task.render_template(
            cls.storage_path,
            cls.task_instance.get_template_context()
        )

        response = kwargs.get('response', {})

        if not isinstance(response, Response):
            raise AirflowException('Result as not HTTP response!')

        if not response.content:
            raise AirflowException('Invalid content!')

        cls.content = response.content

    @classmethod
    def _execute(cls, **kwargs):

        file_path = os.path.join(cls.storage_path, 'captured')
        if not os.path.isdir(file_path):
            os.makedirs(file_path)
        file_path = os.path.join(file_path, '{}.zip'.format(cls.year))

        try:
            f = open(file_path, 'wb')
            f.write(cls.content)
            f.close()
        except Exception as e:
            raise AirflowException('Erro ao gravar arquivo de dados para o ano {}: {}'.format(cls.year, e))

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_captura_produtos(year, **context):
    return SimpleHttpOperator(
        task_id='{}_{}'.format(Tasks.TAREFA_CAPTURA_DADOS_ANUARIO, year),
        http_conn_id=Connections.ANTAQ_HTTP_CONN_ID,
        endpoint='Sistemas/ArquivosAnuario/Arquivos/{}.zip'.format(year),
        method='GET',
        response_check_method=CheckResponseTask.execute,
        response_check_kwargs=dict(
            storage_path=context.get('storage_path'),
            year=year
        ),
        dag=context['dag']
    )
