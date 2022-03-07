# -*- coding: utf-8 -*-

class Variables(object):

    ANTAQ_ETL_DAG_SCHEDULE_INTERVAL = 'antaq_etl_dag_schedule_interval'
    ANTAQ_YEARS_TO_EXTRACT = 'antaq_years_to_extract'

    @classmethod
    def all(cls):
        return {
            # NOTE : Eduardo Luiz
            # Como a periodiciodade de atualização dos dados deve ser mensal
            # vamos carregar todo dia 1 as 0h
            cls.ANTAQ_ETL_DAG_SCHEDULE_INTERVAL: '0 0 1 * *',
            cls.ANTAQ_YEARS_TO_EXTRACT: [2019, 2020, 2021]
        }
