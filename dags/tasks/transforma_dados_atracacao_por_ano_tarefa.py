# -*- coding: utf-8 -*-

import os

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, TimestampType, DecimalType, FloatType
from pyspark.sql.functions import regexp_replace

from airflow.exceptions import AirflowException

from airflow.operators.python_operator import PythonOperator

from tools.tasks.storage_task import StorageTask

from tools.const.tasks import Tasks


class TransformaDadosAtracacao(StorageTask):

    storage_path = None
    storage_path_extracted = None
    storage_path_transformed = None
    data_path = None
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

        cls.storage_path_extracted = os.path.join(cls.storage_path, 'extracted', str(cls.year))
        cls.storage_path_transformed = os.path.join(cls.storage_path, 'transformed', str(cls.year), 'atracacao.parquet')

        try:
            # TODO : Verificar quando o servidor spark estiver em outro HOST
            cls.spark = SparkSession.builder.appName(kwargs['dag'].dag_id).getOrCreate()
        except Exception as e:
            raise AirflowException('Não foi posível conectar com o servidor Spark: {}'.format(e))

    @classmethod
    def _execute(cls, **kwargs):

        # cria atracacao data frame
        atracacao_df = cls.spark.read.csv(
            os.path.join(
                cls.storage_path_extracted,
                '{}Atracacao.txt'.format(cls.year)
            ),
            header='true',
            sep=';'
        )

        # cria atracao tempos data frame
        tempos_atracacao_df = cls.spark.read.csv(
            os.path.join(
                cls.storage_path_extracted,
                '{}TemposAtracacao.txt'.format(cls.year)
            ),
            header='true',
            sep=';'
        )

        # join os dataframes
        atracacao_df = atracacao_df.join(tempos_atracacao_df, ['IDAtracacao'], how='left')

        # ajusta nome das colunas do dataframe
        atracacao_df = atracacao_df\
            .withColumnRenamed('Porto Atracação', 'PortoAtracacao')\
            .withColumnRenamed('Berço', 'Berco')\
            .withColumnRenamed('Apelido Instalação Portuária', 'ApelidoInstalacaoPortuaria')\
            .withColumnRenamed('Complexo Portuário', 'ComplexoPortuario')\
            .withColumnRenamed('Tipo da Autoridade Portuária', 'TipoAutoridadePortuaria')\
            .withColumnRenamed('Data Atracação', 'DataAtracacao')\
            .withColumnRenamed('Data Chegada', 'DataChegada')\
            .withColumnRenamed('Data Desatracação', 'DataDesatracacao')\
            .withColumnRenamed('Data Início Operação', 'DataInicioOperacao')\
            .withColumnRenamed('Data Término Operação', 'DataTerminoOperacao')\
            .withColumnRenamed('Tipo de Operação', 'TipoOperacao')\
            .withColumnRenamed('Tipo de Navegação da Atracação', 'TipoNavegacaoAtracacao')\
            .withColumnRenamed('Nacionalidade do Armador', 'NacionalidadeArmador')\
            .withColumnRenamed('Município', 'Municipio')\
            .withColumnRenamed('Região Geográfica', 'RegiaoGeografica')\
            .withColumnRenamed('Nº da Capitania', 'NumeroCapitania')\
            .withColumnRenamed('Nº do IMO', 'NumeroIMO')

        # ajustando o formado dos campos numéricos
        atracacao_df = atracacao_df\
            .withColumn('TEsperaAtracacao', regexp_replace('TEsperaAtracacao', '\\.', ''))\
            .withColumn('TEsperaAtracacao', regexp_replace('TEsperaAtracacao', ',', '.'))\
            .withColumn('TEsperaInicioOp', regexp_replace('TEsperaInicioOp', '\\.', ''))\
            .withColumn('TEsperaInicioOp', regexp_replace('TEsperaInicioOp', ',', '.'))\
            .withColumn('TOperacao', regexp_replace('TOperacao', '\\.', ''))\
            .withColumn('TOperacao', regexp_replace('TOperacao', ',', '.'))\
            .withColumn('TEsperaDesatracacao', regexp_replace('TEsperaDesatracacao', '\\.', ''))\
            .withColumn('TEsperaDesatracacao', regexp_replace('TEsperaDesatracacao', ',', '.'))\
            .withColumn('TAtracado', regexp_replace('TAtracado', '\\.', ''))\
            .withColumn('TAtracado', regexp_replace('TAtracado', ',', '.'))\
            .withColumn('TEstadia', regexp_replace('TEstadia', '\\.', ''))\
            .withColumn('TEstadia', regexp_replace('TEstadia', ',', '.'))

        # ajusta o tipo das colunas do dataframe
        atracacao_df = atracacao_df\
            .withColumn('IDAtracacao', atracacao_df.IDAtracacao.cast(IntegerType()))\
            .withColumn('CDTUP', atracacao_df.CDTUP.cast(IntegerType()))\
            .withColumn('IDBerco', atracacao_df.IDBerco.cast(IntegerType()))\
            .withColumn('DataAtracacao', atracacao_df.DataAtracacao.cast(TimestampType()))\
            .withColumn('DataChegada', atracacao_df.DataChegada.cast(TimestampType()))\
            .withColumn('DataDesatracacao', atracacao_df.DataDesatracacao.cast(TimestampType()))\
            .withColumn('DataInicioOperacao', atracacao_df.DataInicioOperacao.cast(TimestampType()))\
            .withColumn('DataTerminoOperacao', atracacao_df.DataTerminoOperacao.cast(TimestampType()))\
            .withColumn('Ano', atracacao_df.Ano.cast(IntegerType()))\
            .withColumn('Mes', atracacao_df.Mes.cast(IntegerType()))\
            .withColumn('NacionalidadeArmador', atracacao_df.FlagMCOperacaoAtracacao.cast(IntegerType()))\
            .withColumn('FlagMCOperacaoAtracacao', atracacao_df.FlagMCOperacaoAtracacao.cast(IntegerType()))\
            .withColumn('TEsperaAtracacao', atracacao_df.TEsperaAtracacao.cast(FloatType()))\
            .withColumn('TEsperaInicioOp', atracacao_df.TEsperaInicioOp.cast(FloatType()))\
            .withColumn('TOperacao', atracacao_df.TOperacao.cast(FloatType()))\
            .withColumn('TEsperaDesatracacao', atracacao_df.TEsperaDesatracacao.cast(FloatType()))\
            .withColumn('TAtracado', atracacao_df.TAtracado.cast(FloatType()))\
            .withColumn('TEstadia', atracacao_df.TEstadia.cast(FloatType()))\
            .withColumn('TEsperaAtracacao', atracacao_df.TEsperaAtracacao.cast(DecimalType(15, 15)))\
            # .withColumn('TEsperaInicioOp', atracacao_df.TEsperaInicioOp.cast(DecimalType(15, 15)))\
            # .withColumn('TOperacao', atracacao_df.TOperacao.cast(DecimalType(15, 15)))\
            # .withColumn('TEsperaDesatracacao', atracacao_df.TEsperaDesatracacao.cast(DecimalType(15, 15)))\
            # .withColumn('TAtracado', atracacao_df.TAtracado.cast(DecimalType(15, 15)))\
            # .withColumn('TEstadia', atracacao_df.TEstadia.cast(DecimalType(15, 15)))

        # grava o novo dataframe para o arquivo intermediario
        atracacao_df.write.parquet(cls.storage_path_transformed, mode='overwrite')

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_transforma_dados_atracacao_por_ano(year, **context):
    """ Retorna uma tarefa de transformação dos dados de atracação para o ano informado."""

    return PythonOperator(
        task_id='{}_{}'.format(Tasks.TAREFA_TRANSFORMA_DADOS_ATRACACAO, year),
        python_callable=TransformaDadosAtracacao,
        op_kwargs=dict(
            depends_on=[],
            storage_path=context.get('storage_path'),
            year=year
        ),
        depends_on_past=True,
        provide_context=True,
        dag=context['dag']
    )
