#!/usr/bin/env python
# coding: utf-8

"""
    ``digitaleo`` module
    ====================

    Generic module implementing Digitaleo's APIs consumption

    :Example:

    >>> from digitaleo.auth import OAuth2
    >>> from digitaleo.api import API
    >>> auth = OAuth2(client_id="xxxxxxxxxxxxxxxxx",
    ... client_secret="yyyyyyyyyyyyyyyyyyy")
    >>> api = API(url='contacts.messengeo.net', resource='lists', auth=auth)
    >>> api.read()

"""

import json
import logging
import requests


class API(object):
    """
        Generic API class
    """
    def __init__(self, url, resource, auth=None):
        """
            :param url: API URL base
            :param resource: resource to request
            =param auth: requests.auth object implementing authentication
        """
        self.auth = auth
        self._url = None
        self._resource = None
        self._endpoint = None
        self.url = url
        self.resource = resource

    @property
    def resource(self):
        """ resource property """
        return self._resource

    @resource.setter
    def resource(self, resource):
        self._resource = resource
        self.endpoint = '%s/%s' % (self.url, self.resource)

    @property
    def endpoint(self):
        """ endpoint property """
        return self._endpoint

    @endpoint.setter
    def endpoint(self, endpoint):
        self._endpoint = endpoint

    @property
    def url(self):
        """ url property """
        return self._url

    @url.setter
    def url(self, url):
        self._url = str(url).rstrip('/')
        self.endpoint = '%s/%s' % (self.url, self.resource)

    def __request(self, type='GET', content_type='application/json',
                  dry_run=False, params={}, max_401_retry=3, **kwargs):
        self.type = str.upper(type)

        if dry_run is True:
            logging.debug("This is a dry run mode, skipping %s %s" % (
                self.type, self.endpoint))
            logging.debug("Parameters: %s" % params)
            return "{'message': 'Dry-run mode, request " "%s %s skipped'}" % (
                self.type, self.endpoint)

        logging.debug('%s %s' % (self.type, self.endpoint))
        if params is not None:
            logging.debug('Input params: %s' % params)

        request_arguments = {'params': params.copy(), 'verify': False,
                             'data': {}}
        if 'metaData' in request_arguments['params']:
            request_arguments['params']['metaData'] = json.dumps(
                request_arguments['params']['metaData'])

        if 'complex' in request_arguments['params']:
            try:
                from multidimensional_urlencode import urlencode
                logging.debug('complex key found, doing dirty stuff...')
                complex = urlencode({
                    'complex': request_arguments['params']['complex']})
                self.endpoint += '?%s' % complex
                del(request_arguments['params']['complex'])
            except ImportError as e:
                logging.debug("Unable to handle complex key, missing or"
                              "failed to load multidimensionnal_urlencode: %s"
                              % e)
                raise ValueError("Unable to handle complex filter")

        # XXX: To simplify method calling we only support 'params' as keyword.
        # In case of POST/PUT/DELETE we set params as 'data' keyword of
        # requests library. In case of file uploading, symbolised by the
        # presence of 'files' keyword we let params because contacts API does
        # not support files upload (POST) with parameters in body.
        if self.type.upper() != 'GET' and 'files' not in kwargs:
            action = None
            if 'action' in request_arguments['params']:
                action = request_arguments['params']['action']
                del(request_arguments['params']['action'])

            request_arguments['data'] = json.dumps(
                dict(
                    request_arguments['data'],
                    **request_arguments.pop('params')
                ))
            request_arguments['headers'] = {'Content-type': content_type}

            if action is not None:
                logging.debug("Forcing action parameter to be passed in "
                              "request URL")
                request_arguments['params'] = {'action': action}

        arguments = dict(list(request_arguments.items()) +
                         list(kwargs.items()))

        if self.auth is not None:
            arguments['auth'] = self.auth

        logging.debug("Requests args: %s" % arguments)
        response = getattr(requests, str.lower(self.type))(
            self.endpoint, **arguments)
        logging.debug("URL: %s" % response.url)

        try:
            # Raise an exception onr 4xx, 5xx HTTPError
            response.raise_for_status()
        except Exception as e:

            def process_http_response(response):
                if response.status_code == 500:
                    error = '{"status": 500, "message": "Internal Server '\
                        'Error"}'
                else:
                    error = json.loads(response.text)

                if 'message' in error:
                    details = ""
                    if 'details' in error:
                        details = "(%s)" % error['details']

                    message = "HTTP code <%s>: %s %s" % (response.status_code,
                                                         error,
                                                         details)
                else:  # this is an internal error
                    message = e.message

                return message

            # manage  401
            if response.status_code == 401:
                retry = max_401_retry - 1
                logging.debug("401 'Unauthorized' status code returned, "
                              "retrying a maximum of %s times" % max_401_retry)
                while response.status_code == 401 and retry >= 0:
                    if hasattr(self.auth, 'token'):
                        logging.debug("It looks like authentication mecanism "
                                      "uses token")
                        self.auth.token.expire()

                    response = getattr(requests, str.lower(self.type))(
                        self.url, **arguments)
                    logging.debug("Retry %s/%s: call to %s returned %s"
                                  % (
                                      max_401_retry - retry,
                                      max_401_retry,
                                      response.url,
                                      response.status_code
                                  ))
                    retry -= 1
                try:
                    response.raise_for_status()
                except Exception as e:
                    message = process_http_response(response)
                    logging.debug(message)
                    raise Exception(message)
            else:
                message = process_http_response(response)
                raise Exception(message)

        logging.debug("HTTP code <%s>: OK" % response.status_code)

        text = response.text or '{}'
        return json.loads(text)

    def request(self, **kwargs):
        return self.__request(**kwargs)

    def post(self, **kwargs):
        return self.__request(type='POST', **kwargs)

    def create(self, **kwargs):
        return self.post(**kwargs)

    def read(self, **kwargs):
        return self.get(**kwargs)

    def get(self, **kwargs):
        return self.__request(type='GET', **kwargs)

    def update(self, **kwargs):
        return self.put(**kwargs)

    def put(self, **kwargs):
        return self.__request(type='PUT', **kwargs)

    def delete(self, **kwargs):
        return self.__request(type='DELETE', **kwargs)
