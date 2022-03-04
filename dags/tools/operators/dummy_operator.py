# -*- coding: utf-8 -*-

from airflow.operators.dummy_operator import DummyOperator


def get_task_dummy_operator(task_id, trigger_rule='all_success', **context):
    return DummyOperator(
        task_id=task_id,
        trigger_rule=trigger_rule,
        dag=context.get('dag')
    )
