# -*- coding: utf-8 -*-

import logging

from airflow.exceptions import AirflowException
from airflow.utils.decorators import apply_defaults

from ..hooks.http_hook import HttpHook
from .abstract_operator import AbstractOperator


class SimpleHttpOperator(AbstractOperator):
    """
    Calls an endpoint on an HTTP system to execute an action

    :param http_conn_id: The connection to run the sensor against
    :type http_conn_id: string
    :param endpoint: The relative part of the full url
    :type endpoint: string
    :param method: The HTTP method to use, default = "POST"
    :type method: string
    :param data: The data to pass. POST-data in POST/PUT and params
        in the URL for a GET request.
    :type data: For POST/PUT, depends on the content-type parameter,
        for GET a dictionary of key/value string pairs
    :param headers: The HTTP headers to be added to the GET request
    :type headers: a dictionary of string key/value pairs
    :param response_check: A check against the 'requests' response object.
        Returns True for 'pass' and False otherwise.
    :type response_check: A lambda or defined function.
    :param extra_options: Extra options for the 'requests' library, see the
        'requests' documentation (options to modify timeout, ssl, etc.)
    :type extra_options: A dictionary of options, where key is string and value
        depends on the option that's being modified.
    """

    template_fields = ('endpoint', 'data',)
    template_ext = ()
    ui_color = '#f4a460'

    @apply_defaults
    def __init__(self,
                 endpoint,
                 endpoint_method=None,
                 endpoint_method_kwargs=None,
                 method='POST',
                 data=None,
                 data_method=None,
                 data_method_kwargs=None,
                 headers=None,
                 headers_method=None,
                 headers_method_kwargs=None,
                 session=None,
                 session_method=None,
                 session_method_kwargs=None,
                 response_check_method=None,
                 response_check_kwargs=None,
                 extra_options=None,
                 xcom_push=False,
                 http_conn_id='http_default',
                 *args,
                 **kwargs):
        """
        If xcom_push is True, response of an HTTP request will also
        be pushed to an XCom.
        """
        super(SimpleHttpOperator, self).__init__(*args, **kwargs)
        self.http_conn_id = http_conn_id
        self.method = method
        self.endpoint = endpoint
        self.endpoint_method = endpoint_method
        self.endpoint_method_kwargs = endpoint_method_kwargs or {}
        self.data = data or {}
        self.data_method = data_method
        self.data_method_kwargs = data_method_kwargs or {}
        self.headers = headers or {}
        self.headers_method = headers_method
        self.headers_method_kwargs = headers_method_kwargs or {}
        self.session = session or {}
        self.session_method = session_method
        self.session_method_kwargs = session_method_kwargs or {}
        self.response_check_method = response_check_method
        self.response_check_kwargs = response_check_kwargs or {}
        self.extra_options = extra_options or {}
        self.xcom_push_flag = xcom_push

    def _execute(self, **context):

        if self.data_method:
            kwargs = dict(self.data_method_kwargs)
            kwargs.update(context)
            data = self.data_method(**kwargs)
        else:
            data = self.data

        if self.headers_method:
            kwargs = dict(self.headers_method_kwargs)
            kwargs.update(context)
            headers = self.headers_method(**kwargs)
        else:
            headers = self.headers

        if self.session_method:
            kwargs = dict(self.session_method_kwargs)
            kwargs.update(context)
            session = self.session_method(**kwargs)
        else:
            session = self.session

        if self.endpoint_method:
            kwargs = dict(self.endpoint_method_kwargs)
            kwargs.update(context)
            endpoint = self.endpoint_method(**kwargs)
        else:
            endpoint = self.endpoint

        logging.info("Calling HTTP method.")

        http = HttpHook(
            self.method,
            http_conn_id=self.http_conn_id
        )

        response = http.run(
            endpoint,
            data,
            headers,
            self.extra_options,
            session=session
        )

        result = None
        if self.response_check_method:
            kwargs = dict(self.response_check_kwargs)
            kwargs.update(context)
            kwargs.update({'session': session})
            result = self.response_check_method(response=response, **kwargs)
            if not result:
                raise AirflowException("Response check returned False.")

        if self.xcom_push_flag and result:
            return result

        return True
