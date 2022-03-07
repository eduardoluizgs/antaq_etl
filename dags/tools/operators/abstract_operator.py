# -*- coding: utf-8 -*-

from collections import defaultdict

from airflow.models import BaseOperator


class AbstractOperator(BaseOperator):

    def execute(self, **kwargs):
        self._pre_execute(**kwargs)
        result = self._execute(**kwargs)
        return self._post_execute(**kwargs) or result

    def _pre_execute(self, **kwargs):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method
            Default approach should exists here like get task_config """

        context = dict(kwargs.get('context', {}))

        # get default params
        self.task_instance = context.get('task_instance', None)
        self.depends_on = context.get('depends_on', None)

        # get task config from default kwargs (for tests and mocks)
        self.task_config = kwargs.get('task_config', None)

        # if not pass task_config, lets get from task instance
        if not self.task_config and self.depends_on:
            self.task_config = defaultdict(list)
            for config in self.task_instance.xcom_pull(task_ids=self.depends_on):
                if config and isinstance(config, dict):
                    for key, value in config.items():
                        self.task_config[key].append(value)

    def _execute(self, **kwargs):
        return None

    def _post_execute(self, **kwargs):
        return None
