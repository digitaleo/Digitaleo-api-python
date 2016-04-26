#!/usr/bin/env python
# coding: utf-8

"""
    ``digitaleo.auth`` module
    ====================

    Auth module used for Digitaleo API authentication

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
from requests.auth import AuthBase
from requests.packages.urllib3.exceptions import InsecureRequestWarning
from datetime import datetime, timedelta

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class Token(object):
    """
        Base class implementing usefull method for generic token management
    """

    def __init__(self, access=None, refresh=None, expires_in=None):
        """
            :param access: The token access
            :param refresh: The refresh token
            :param expires_in: Token duration validity in seconds
            :type access: string
            :type refresh: string
            :type expires_in: int
        """
        self.access_token = access
        self.refresh_token = refresh
        self.expires_in = expires_in
        self.printable_attributes = ['access_token', 'refresh_token',
                                     'expires_in']
        self.expiration = None
        self.original_json = None

    def load_from_json(self, json={}):
        """
            Parse a JSON string and set values to object attributes
            :param json: JSON string to parese
            :type access: string
        """

        self.original_json = json
        for key in self.__dict__.keys():
            if key in json:
                setattr(self, key, json[key])

        self.set_expiration()

    def set_expiration(self):
        """
            Compute expiration date using expires_in attribute
        """
        # This is an arbitrary decision setting the expiration time
        # to the current date + expires_in - 10 seconds
        self.expiration = datetime.now() + \
            timedelta(seconds=(self.expires_in - 10))
        logging.debug('Token expiration set to %s' % self.expiration)

    def is_expired(self):
        """
            Method evaluating expiration of a token
            :return: True or False
        """
        if self.access_token is None:
            logging.debug('Access token not found')
            return True
        else:
            return (self.expiration <= datetime.now())

    def expire(self):
        """
            Force token expiration (object side)
        """
        logging.debug("Expiring token as wanted...")
        self.expiration = datetime.now() - timedelta(seconds=(10))

    def __str__(self):
        """
            JSON representation of Token object
            :return: JSON string
        """
        if self.original_json is not None:
            return json.dumps(self.original_json)

        printable_dict = {}
        for key in self.printable_attributes:
            printable_dict[key] = getattr(self, key)

        return json.dumps(printable_dict)


class OAuth2Base(AuthBase):
    """
        OAuth2 base class subclassing ``requests.auth.AuhtBase``
    """

    def __init__(self):
        self.token = Token()

    def __get_token_data__(self):
        """
            Method retrieving a JSON string representing a valid ``Token``
            object
            :rtype: JSON string
        """
        raise Exception("Implement me!")

    def get_access_token(self):
        """
            Method returning the access token, autmatically invoke
            __get_token_data__ method if token is expired
            :return: The access token
            :rtype: string
        """
        if self.token.is_expired():
            logging.debug('Requesting a new access token')
            self.token.load_from_json(json=self.__get_token_data__())
        else:
            logging.debug('Access token still valid')

        return self.token.access_token

    def __call__(self, r):
        """
            Implement method called by requests.auth
        """
        r.headers['Authorization'] = 'Bearer %s' % self.get_access_token()
        return r


class OAuth2(OAuth2Base):
    """
        Digitaleo OAuth2 implementation
    """
    def __init__(self, grant_type='client_credentials', client_id=None,
                 client_secret=None, login=None, password=None):
        """
            :param grant_type: grant type request, default is
            'client_credentials'
            :param client_id: The client id
            :param client_secret: The client secret
        """
        self.url = 'https://oauth.messengeo.net'
        self.grant_type = grant_type
        self.client_id = client_id
        self.client_secret = client_secret
        self.login = login
        self.password = password

        return super(OAuth2, self).__init__()

    def __get_token_data__(self):
        url = '%s/token' % self.url
        data = {'grant_type': self.grant_type}
        headers = {'content-type': 'application/x-www-form-urlencoded'}

        if self.grant_type == 'client_credentials':
            data['client_id'] = self.client_id
            data['client_secret'] = self.client_secret

        response = requests.post(url, data=data, headers=headers)
        try:
            response.raise_for_status()
        except Exception:
            raise Exception("Unable to get access_token: %s" %
                            response.json()['error'])

        return response.json()
