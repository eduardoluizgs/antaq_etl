# -*- coding: utf-8 -*-

import os

from pyspark.sql import SparkSession

from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook

from airflow.exceptions import AirflowException

from airflow.models import Variable as AirflowVariables
from airflow.operators.python_operator import PythonOperator

from tools.tasks.storage_task import StorageTask

from tools.const.variabels import Variables
from tools.const.tasks import Tasks


class GravaDadosAtracacao(StorageTask):

    storage_path = None
    storage_path_transformed = None
    year = None
    spark = None

    @classmethod
    def _pre_execute(cls, **kwargs):

        super()._pre_execute(**kwargs)

        cls.storage_path = kwargs.get('storage_path', None)
        if not cls.storage_path:
            raise AirflowException('Invalid Storage Path!')

        cls.year = kwargs.get('year', None)
        if not cls.year:
            raise AirflowException('Invalid Year!')

        t = cls.task_instance.task.render_template(
            cls.storage_path,
            cls.task_instance.get_template_context()
        )

        cls.storage_path_transformed = os.path.join(cls.storage_path, 'transformed', str(cls.year), 'atracacao.parquet')

        try:
            # TODO : Verificar quando o servidor spark estiver em outro HOST
            cls.spark = SparkSession.builder.appName(kwargs['dag'].dag_id).getOrCreate()
        except Exception as e:
            raise AirflowException('Não foi posível conectar com o servidor Spark: {}'.format(e))

    @classmethod
    def _execute(cls, **kwargs):

        mssql_hook = MsSqlHook(mssql_conn_id='mssql_default')

        # captura os dados de atracacao gravados anteriormente
        atracacao_df = cls.spark.read.parquet(cls.storage_path_transformed)

        '''
        # TIP : use isto para criar a estrutura da tabela de destino
        for column_name, column_type in atracacao_df.dtypes:
            if column_type == 'string':
                data_type = 'NVARCHAR(255)'
            elif column_type == 'int':
                data_type = 'INT'
            elif column_type == 'float':
                data_type = 'DECIMAL(36, 18)'
            elif column_type == 'timestamp':
                data_type = 'DATETIME'
            else:
                raise Exception('Column type is not defined!')

            print('{} {} NULL,'.format((column_name + (' ' * 33))[:33], data_type))
        '''

        '''
        # TIP : Use isto para debug a inserção linha a linha
        for row in atracacao_df.toLocalIterator():

            rows = [tuple(row.asDict().values())]

            print('Inserting new record...')
            for i in range(len(atracacao_df.columns)):
                print('{}: {} - {}'.format(atracacao_df.columns[i], rows[0][i], atracacao_df.dtypes[i][1]))
            print('\n')

            # grava os novos registros da tabela
            mssql_hook.insert_rows(
                table='atracacao_fato',
                rows=rows,
                target_fields=atracacao_df.columns,
                commit_every=1
        #     )
        '''

        # NOTE : Eduardo Luiz
        # Necessário um método mais otimizado de UPSERT para evitar remover todas as linhas da tabela.

        # limpa os registros da tabela para o ano atual
        mssql_hook.run("DELETE FROM dbo.atracacao_fato WHERE ano = {}".format(cls.year))

        # grava os novos registros da tabela
        mssql_hook.insert_rows(
            table='atracacao_fato',
            rows=atracacao_df.toLocalIterator(),
            target_fields=atracacao_df.columns,
            commit_every=1000
        )

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_grava_dados_atracacao_por_ano(year, **context):
    """ Retorna uma tarefa de transformação dos dados de atracação para o ano informado."""

    return PythonOperator(
        task_id='{}_{}'.format(Tasks.TAREFA_GRAVA_DADOS_ATRACACAO, year),
        python_callable=GravaDadosAtracacao,
        op_kwargs=dict(
            depends_on=[],
            storage_path=context.get('storage_path'),
            year=year
        ),
        depends_on_past=True,
        provide_context=True,
        dag=context['dag']
    )
