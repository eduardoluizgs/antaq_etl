# -*- coding: utf-8 -*-

class Connections(object):

    SQLSERVER_CONN_ID = 'sql_server'

    @classmethod
    def all(cls):
        return {
            cls.SQLSERVER_CONN_ID: {
                'type': 'http',
                'uri': ''
            }
        }
