# -*- coding: utf-8 -*-

from multiprocessing.sharedctypes import Value
import os

from pyspark.sql import SparkSession
from pyspark.sql.types import IntegerType, TimestampType, DecimalType, FloatType, BooleanType
from pyspark.sql.functions import regexp_replace, year, month, lit, when

from airflow.exceptions import AirflowException

from airflow.operators.python_operator import PythonOperator

from tools.tasks.storage_task import StorageTask

from tools.const.tasks import Tasks


class TransformaDadosCarga(StorageTask):

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
        cls.storage_path_transformed = os.path.join(cls.storage_path, 'transformed', str(cls.year), 'carga.parquet')

        try:
            # TODO : Verificar quando o servidor spark estiver em outro HOST
            cls.spark = SparkSession.builder.appName(kwargs['dag'].dag_id).getOrCreate()
        except Exception as e:
            raise AirflowException('Não foi posível conectar com o servidor Spark: {}'.format(e))

    @classmethod
    def _execute(cls, **kwargs):

        # cria atracacao dataframe
        carga_df = cls.spark.read.csv(
            os.path.join(
                cls.storage_path_extracted,
                '{}Carga.txt'.format(cls.year)
            ),
            header='true',
            sep=';'
        )

        # cria carga conteirizada dataframe
        carga_conteirizada_df = cls.spark.read.csv(
            os.path.join(
                cls.storage_path_extracted,
                '{}Carga_Conteinerizada.txt'.format(cls.year)
            ),
            header='true',
            sep=';'
        )

        # cria atracao tempos dataframe
        atracacao_df = cls.spark.read.csv(
            os.path.join(
                cls.storage_path_extracted,
                '{}Atracacao.txt'.format(cls.year)
            ),
            header='true',
            sep=';'
        )

        # join os dataframes
        carga_df = carga_df.join(carga_conteirizada_df, ['IDCarga'], how='left')
        carga_df = carga_df.join(atracacao_df, ['IDAtracacao'], how='inner')

        # remove colunas que não são necessárias
        carga_df = carga_df.drop(*(
            'CDTUP',
            'IDBerco',
            'Berço',
            'Apelido Instalação Portuária',
            'Complexo Portuário',
            'Tipo da Autoridade Portuária',
            'Data Atracação',
            'Data Chegada',
            'Data Desatracação',
            'Data Término Operação',
            'Ano',
            'Mes',
            'Tipo de Operação',
            'Tipo de Navegação da Atracação',
            'Nacionalidade do Armador',
            'FlagMCOperacaoAtracacao',
            'Terminal',
            'Município',
            'UF',
            'Região Geográfica',
            'Nº da Capitania',
            'Nº do IMO'
        ))

        # ajusta nome das colunas do dataframe
        carga_df = carga_df\
            .withColumnRenamed('Tipo Operação da Carga', 'TipoOperacaoCarga')\
            .withColumnRenamed('Carga Geral Acondicionamento', 'CargaGeralAcondicionamento')\
            .withColumnRenamed('Tipo Navegação', 'TipoNavegacao')\
            .withColumnRenamed('Percurso Transporte em vias Interiores', 'PercursoTransporteViasInteriores')\
            .withColumnRenamed('Percurso Transporte Interiores', 'PercursoTransporteInteriores')\
            .withColumnRenamed('Natureza da Carga', 'NaturezaCarga')\
            .withColumnRenamed('Porto Atracação', 'PortoAtracacao')\
            .withColumnRenamed('Data Início Operação', 'DataInicioOperacao')

        # ajustando o formado dos campos numéricos
        carga_df = carga_df\
            .withColumn('FlagAutorizacao', regexp_replace('FlagAutorizacao', 'S', '1'))\
            .withColumn('FlagAutorizacao', regexp_replace('FlagAutorizacao', 'N', '0'))\
            .withColumn('FlagAutorizacao', regexp_replace('FlagAutorizacao', 'null', '0'))\
            .withColumn('FlagCabotagemMovimentacao', regexp_replace('FlagCabotagemMovimentacao', 'null', '0'))\
            .withColumn('FlagConteinerTamanho', regexp_replace('FlagConteinerTamanho', 'null', '0'))\
            .withColumn('FlagLongoCurso', regexp_replace('FlagLongoCurso', 'null', '0'))\
            .withColumn('FlagMCOperacaoCarga', regexp_replace('FlagMCOperacaoCarga', 'null', '0'))\
            .withColumn('FlagOffshore', regexp_replace('FlagOffshore', 'null', '0'))\
            .withColumn('FlagTransporteViaInterioir', regexp_replace('FlagTransporteViaInterioir', 'null', '0'))\
            .withColumn('VLPesoCargaBruta', regexp_replace('VLPesoCargaBruta', '\\.', ''))\
            .withColumn('VLPesoCargaBruta', regexp_replace('VLPesoCargaBruta', ',', '.'))\
            .withColumn('PesoLiquidoCarga', lit(0))

        # ajusta o tipo das colunas do dataframe
        carga_df = carga_df\
            .withColumn('IDCarga', carga_df.IDCarga.cast(IntegerType()))\
            .withColumn('IDAtracacao', carga_df.IDAtracacao.cast(IntegerType()))\
            .withColumn('CDMercadoria', carga_df.CDMercadoria.cast(IntegerType()))\
            .withColumn('FlagAutorizacao', carga_df.FlagAutorizacao.cast(BooleanType()))\
            .withColumn('FlagCabotagem', carga_df.FlagCabotagem.cast(BooleanType()))\
            .withColumn('FlagCabotagemMovimentacao', carga_df.FlagCabotagemMovimentacao.cast(BooleanType()))\
            .withColumn('FlagConteinerTamanho', carga_df.FlagConteinerTamanho.cast(BooleanType()))\
            .withColumn('FlagLongoCurso', carga_df.FlagLongoCurso.cast(BooleanType()))\
            .withColumn('FlagMCOperacaoCarga', carga_df.FlagMCOperacaoCarga.cast(BooleanType()))\
            .withColumn('FlagOffshore', carga_df.FlagOffshore.cast(BooleanType()))\
            .withColumn('FlagTransporteViaInterioir', carga_df.FlagTransporteViaInterioir.cast(BooleanType()))\
            .withColumn('TEU', carga_df.TEU.cast(IntegerType()))\
            .withColumn('QTCarga', carga_df.QTCarga.cast(IntegerType()))\
            .withColumn('VLPesoCargaBruta', carga_df.VLPesoCargaBruta.cast(FloatType()))\
            .withColumn('DataInicioOperacao', carga_df.DataInicioOperacao.cast(TimestampType()))\
            .withColumn('PesoLiquidoCarga', carga_df.PesoLiquidoCarga.cast(FloatType()))

        # cria colunas do inicio da operacao
        carga_df = carga_df\
            .withColumn('AnoInicioOperacao', year(carga_df.DataInicioOperacao))\
            .withColumn('MesInicioOperacao', month(carga_df.DataInicioOperacao))\
            .withColumn('PesoLiquidoCarga', lit(0))

        # ajusta o código da mercadoria e peso para produtos conteuberuzados
        carga_df = carga_df\
            .withColumn('CDMercadoria',
                when(carga_df.CargaGeralAcondicionamento == 'Conteinerizada', carga_df.CDMercadoriaConteinerizada)\
                    .otherwise(carga_df.CDMercadoria)
            )\
            .withColumn('PesoLiquidoCarga',
                when(carga_df.CargaGeralAcondicionamento == 'Conteinerizada', carga_df.VLPesoCargaConteinerizada)\
                    .otherwise(carga_df.VLPesoCargaBruta)
            )

        # remove colunas que não são necessárias
        carga_df = carga_df.drop(*(
            'CDMercadoriaConteinerizada',
            'VLPesoCargaConteinerizada',
            'DataInicioOperacao',
        ))

        # grava o novo dataframe para o arquivo intermediario
        carga_df.write.parquet(cls.storage_path_transformed, mode='overwrite')

        return True

    @classmethod
    def _post_execute(cls, **kwargs):
        return True


def get_tarefa_transforma_dados_carga_por_ano(year, **context):
    """ Retorna uma tarefa de transformação dos dados de cargas para o ano informado."""

    return PythonOperator(
        task_id='{}_{}'.format(Tasks.TAREFA_TRANSFORMA_DADOS_CARGA, year),
        python_callable=TransformaDadosCarga,
        op_kwargs=dict(
            depends_on=[],
            storage_path=context.get('storage_path'),
            year=year
        ),
        depends_on_past=True,
        provide_context=True,
        dag=context['dag']
    )
