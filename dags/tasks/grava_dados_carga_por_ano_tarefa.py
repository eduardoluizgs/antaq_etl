# -*- coding: utf-8 -*-

import os

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when

from airflow.providers.microsoft.mssql.hooks.mssql import MsSqlHook
from airflow.providers.microsoft.mssql.operators.mssql import MsSqlOperator

from airflow.exceptions import AirflowException

from airflow.models import Variable as AirflowVariables
from airflow.operators.python_operator import PythonOperator

from tools.tasks.storage_task import StorageTask

from tools.const.variabels import Variables
from tools.const.tasks import Tasks


class GravaDadosCarga(StorageTask):

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

        cls.storage_path_transformed = os.path.join(cls.storage_path, 'transformed', str(cls.year), 'carga.parquet')

        try:
            # TODO : Verificar quando o servidor spark estiver em outro HOST
            # NOTE : Verificar o melhor lugar para realizar a configuração de memória
            cls.spark = SparkSession.builder\
                .appName(kwargs['dag'].dag_id)\
                .config('spark.driver.memory', '10g')\
                .getOrCreate()
        except Exception as e:
            raise AirflowException('Não foi posível conectar com o servidor Spark: {}'.format(e))

    @classmethod
    def _execute(cls, **kwargs):

        mssql_hook = MsSqlHook(mssql_conn_id='mssql_default')

        # captura os dados de atracacao gravados anteriormente
        carga_df = cls.spark.read.parquet(cls.storage_path_transformed)

        '''
        # TIP : use isto para criar a estrutura da tabela de destino
        for column_name, column_type in carga_df.dtypes:
            if column_type == 'string':
                data_type = 'NVARCHAR(255)'
            elif column_type == 'int':
                data_type = 'INT'
            elif column_type == 'float':
                data_type = 'NUMERIC(15, 2)'
            elif column_type == 'timestamp':
                data_type = 'DATETIME'
            elif column_type == 'boolean':
                data_type = 'BIT'
            else:
                raise Exception('Column type is not defined!')

            print('{} {} NULL,'.format((column_name + (' ' * 33))[:33], data_type))
        '''

        # NOTE : Eduardo Luiz
        # Necessário um método mais otimizado de UPSERT para evitar remover todas as linhas da tabela.
        # Talvez uma tarefa anterior somente para remover os dados da tabela
        # ou uma logica SQL para atualizar e inserir se não houver

        # limpa os registros da tabela para as atracações do ano atual
        mssql_hook.run('''
                DELETE carga FROM dbo.carga_fato AS carga
                INNER JOIN dbo.atracacao_fato AS atracacao ON atracacao.IDAtracacao = carga.IDAtracacao
                WHERE atracacao.ano = {}
            '''.format(cls.year)
        )

        cls.log.info('Total de registros: {}...'.format(carga_df.count()))

        # NOTE : Eduardo Luiz
        # É interessante testes a gravação dos dados usando o método bulk_load
        # verificando se o método é mais rápido

        # grava os novos registros da tabela
        mssql_hook.insert_rows(
            table='carga_fato',
            rows=carga_df.toLocalIterator(),
            target_fields=carga_df.columns,
            commit_every=1000
        )

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_grava_dados_carga_por_ano(year, **context):
    """ Retorna uma tarefa de transformação dos dados de carga para o ano informado."""

    return PythonOperator(
        task_id='{}_{}'.format(Tasks.TAREFA_GRAVA_DADOS_CARGA, year),
        python_callable=GravaDadosCarga,
        op_kwargs=dict(
            depends_on=[],
            storage_path=context.get('storage_path'),
            year=year
        ),
        depends_on_past=True,
        provide_context=True,
        dag=context['dag']
    )
