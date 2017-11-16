from flask import g
from flask_restplus import abort
from flask_httpauth import HTTPBasicAuth, HTTPTokenAuth, MultiAuth
from app.models import User

class Auth():
    """
    Authorization via basic auth or bearer token. Call methods as decorators.

    :var     basic_auth: Authorization via basic auth
    :vartype basic_auth: flask_httpauth.HTTPBasicAuth
    :var     token_auth: Authorization via bearer token
    :vartype token_auth: flask_httpauth.HTTPTokenAuth
    :var     multi_auth: Authorization via basic auth or bearer token
    :vartype multi_auth: flask_httpauth.MultiAuth
    """
    basic_auth = HTTPBasicAuth()
    token_auth = HTTPTokenAuth('Bearer')
    multi_auth = MultiAuth(basic_auth, token_auth)

    @staticmethod
    @basic_auth.verify_password
    def verify_password(username, password):
        """
        Verify user password in basic auth. Called this method in use of
        @basic_auth.login_required or @multi_auth.login_required decorators

        :param username: User login
        :type  username: str
        :param password: User password
        :type  password: str
        :return: True if the password matched, False otherwise
        :rtype:  bool
        """
        user = User.query.filter_by(username = username).first()
        if not user or not user.verify_password(password):
            return False
        # Insert authorized user in Flask g object
        g.user = user
        return True

    @staticmethod
    @token_auth.verify_token
    def verify_token(token):
        """
        Verify user password in bearer token auth. Called this method in use of
        @token_auth.login_required or @multi_auth.login_required decorators

        :param token: Bearer token
        :type  token: str
        :return: True if the token matched, False otherwise
        :rtype:  bool
        """
        user = User.verify_auth_token(token)
        if not user:
            return False
        # Insert authorized user in Flask g object
        g.user = user
        return True

    @staticmethod
    @token_auth.error_handler
    @basic_auth.error_handler
    def unauthorized():
        """
        Return error JSON in 401 response if authorization is failed
        """
        abort(401, message="Unauthorized access")