# -*- coding: utf-8 -*-

import logging

from collections import defaultdict


MSG_INVALID_TASK_CONFIG = 'Invalid task config! Task config is required for this task!'


class AbstractTask(object):

    log = logging.getLogger(__name__)

    depends_on = None
    task_instance = None
    task_config = None

    def __new__(cls, *args, **kwargs):
        return cls.execute(*args, **kwargs)

    @classmethod
    def execute(cls, *args, **kwargs):
        cls._pre_execute(**kwargs)
        result = cls._execute(**kwargs)
        return cls._post_execute(**kwargs) or result

    @classmethod
    def check(cls, **kwargs):
        return True

    @classmethod
    def _pre_execute(cls, **kwargs):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method
            Default approach should exists here like get task_config """

        context = kwargs.get('context', kwargs)

        # get default params
        cls.task_instance = context.get('task_instance', None)

        # get task config from default kwargs (for tests and mocks)
        cls.task_config = kwargs.get('task_config', None)

        # get dependentes tasks
        cls.depends_on = kwargs.get('depends_on', None)

        # if not pass task_config, lets get from task instance
        if not cls.task_config and cls.depends_on:
            cls.task_config = defaultdict(dict)
            for config in cls.task_instance.xcom_pull(task_ids=cls.depends_on):
                if config and isinstance(config, dict):
                    for key, value in config.items():
                        cls.task_config[key] = value

    @classmethod
    def _pre_validate(cls, **kwargs):
        """ Pre execute logic. This method is executed before the main logic in the 'execute' method """
        pass

    @classmethod
    def _execute(cls, **kwargs):
        """ Execute the main logic here """
        raise Exception('Not implemented! This method have implemented in child class!')

    @classmethod
    def _post_execute(cls, **kwargs):
        """ Post execute logic. This method is executed after the main logic in the 'execute' method """
        return None
