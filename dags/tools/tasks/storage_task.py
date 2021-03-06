# -*- coding: utf-8 -*-

from .abstract_task import AbstractTask


MSG_INVALID_TASK_CONFIG = 'Invalid task config! Task config is required for this task!'
MSG_INVALID_STORAGE = 'Invalid storage parameter! Storage parameter is required for this task!'


class StorageTask(AbstractTask):

    storage = None

    @classmethod
    def get_storage(cls, storage_name):

        # get storage object
        storage = cls.storage[storage_name].get('object', None)
        if storage is None:
            raise Exception(
                'Invalid object from storage!'
                'Check the source of content in previous tasks: {}'.format(
                    storage_name
                )
            )

        return storage
