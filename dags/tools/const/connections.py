# -*- coding: utf-8 -*-

class Connections(object):

    SQLSERVER_CONN_ID = 'sql_server'
    ANTAQ_HTTP_CONN_ID = 'antaq_http'

    @classmethod
    def all(cls):
        return {
            cls.SQLSERVER_CONN_ID: {
                'type': 'mssql',
                'uri': ''
            },
            cls.ANTAQ_HTTP_CONN_ID: {
                'type': 'mssql',
                'uri': 'http://web.antaq.gov.br'
            }
        }
