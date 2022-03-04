# -*- coding: utf-8 -*-

import subprocess

from airflow.settings import Session
from airflow.models import Variable, Connection


def check_variables(variables):
    for key, value in variables.items():
        try:
            Variable.get(key)
        except:
            Variable.set(
                key,
                value,
                serialize_json=(isinstance(value, list) or isinstance(value, dict))
            )

def check_connections(connections):
    for connection, params in connections.items():
        exists = Session().query(Connection)\
            .filter(Connection.conn_id == connection)\
            .count()
        if not exists:
            subprocess.Popen(
                "python $AIRFLOW_HOME/bin/airflow connections --add --conn_id '{}' --conn_type '{}' --conn_uri '{}'".format(
                    connection,
                    params.get('type', ' '),
                    params.get('uri', ' ')
                ),
                shell=True
            )
