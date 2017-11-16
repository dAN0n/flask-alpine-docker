from flask import g
from flask_restplus import Namespace, Resource, fields, marshal, abort
from sqlalchemy.exc import IntegrityError
from app import db
from app.models import User
from app.FtsRequest import FtsRequest
from app.rest.Auth import Auth

# Define namespace
api = Namespace('Users', description='Operations with users', path='/')

### JSON Parsers ###

# Request JSON fields
user_request = api.parser()
user_request.add_argument('username', type = str, location = 'json')
user_request.add_argument('password', type = str, location = 'json')
user_request.add_argument('phone', type = str, location = 'json')
user_request.add_argument('fts_key', type = int, location = 'json')

# Request JSON fields (all fields required)
user_request_required = api.parser()
user_request_required.add_argument('username', type = str, required = True,
    help = 'No username provided', location = 'json')
user_request_required.add_argument('password', type = str, required = True,
    help = 'No password provided', location = 'json')
user_request_required.add_argument('phone', type = str, required = True,
    help = 'No phone provided', location = 'json')
user_request_required.add_argument('fts_key', type = int, required = True,
    help = 'No fts_key provided', location = 'json')

### JSON Models ###

# Request JSON template
user_request_fields = api.model('Users request',
{
    'username': fields.String(description='Login'),
    'password': fields.String(description='Password'),
    'phone': fields.String(description='Phone number'),
    'fts_key': fields.Integer(description='Federal Tax Service key from SMS'),
})

# Request JSON template (all fields required)
user_request_required_fields = api.model('Users request (all fields required)',
{
    'username': fields.String(description='Login', required=True),
    'password': fields.String(description='Password', required=True),
    'phone': fields.String(description='Phone number', required=True),
    'fts_key': fields.Integer(description='Federal Tax Service key from SMS', required=True),
})

# Response JSON template
user_fields = api.model('Users response',
{
    'id': fields.Integer(description='ID', required = True),
    'username': fields.String(description='Login', required = True),
    'phone': fields.String(description='Phone number', required = True),
})

@api.route('/users', endpoint = 'users')
class UserList(Resource):
    """
    Operations with list of users
    """
    @api.doc(security = None)
    @api.expect(user_request_required_fields)
    @api.marshal_with(user_fields, envelope = 'user', code = 201)
    @api.doc(responses = {
        400: 'No username/password/phone/fts_key provided',
        404: "Can't authorize in Federal Tax Service with given phone/key",
        409: 'Username already exist',
    })
    def post(self):
        """
        Create new user in database

        :return: New user with some data
        :rtype:  dict/json
        """
        # Parsing request JSON fields
        args = user_request_required.parse_args()
        # Error checking
        self.abortIfFtsUserDoesntExist(args['phone'], args['fts_key'])
        # Create user and add to database
        user = User(
            username = args['username'],
            phone = args['phone'],
            fts_key = args['fts_key'])
        user.hash_password(args['password'])
        try:
            db.session.add(user)
            db.session.commit()
            # Return JSON using template
            return user, 201
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Username '{}' already exist".format(args['username']))

    @staticmethod
    def abortIfFtsUserDoesntExist(phone, fts_key):
        """
        Return error JSON in 409 response if user doesn't exists in Federal Tax Service

        :param username: User phone number
        :type  username: str
        :param username: SMS key
        :type  username: int
        """
        fts = FtsRequest()
        if fts.checkAuthData(phone, fts_key) is False:
            abort(404, message="Can't authorize in Federal Tax Service with given phone/key")

@api.route('/users/<int:id>', endpoint = 'user')
@api.param('id', 'User ID in database')
class Users(Resource):
    """
    Operations with user selected by id

    :var     method_decorators: Decorators applied to methods
    :vartype method_decorators: list
    """
    method_decorators = [Auth.multi_auth.login_required]

    @api.marshal_with(user_fields, envelope='user')
    @api.doc(responses = {
        401: 'Unauthorized access',
        404: "User id doesn't exist",
    })
    def get(self, id):
        """
        Get user partial info with provided id

        :return: User with some data
        :rtype:  dict/json
        """
        user = User.query.get(id)
        # Error checking
        self.abortIfUserDoesntExist(user, id)
        # Return JSON using template
        return user

    @staticmethod
    def abortIfUserDoesntExist(user, id):
        """
        Return error JSON in 404 response if user doesn't exists in database

        :param user: User from database
        :type  user: app.models.User
        :param id: User id
        :type  id: int
        """
        if user is None:
            abort(404, message="User id {} doesn't exist".format(id))

@api.route('/users/me', endpoint = 'userme')
class UserInfo(Resource):
    """
    Operations with authorized user

    :var     method_decorators: Decorators applied to methods
    :vartype method_decorators: list
    """
    method_decorators = [Auth.multi_auth.login_required]

    @api.marshal_with(user_fields, envelope='user')
    @api.response(401, 'Unauthorized access')
    def get(self):
        """
        Get authorized user partial info

        :return: User with some data
        :rtype:  dict/json
        """
        # Login of authorized user stores in Flask g object
        user = User.query.filter_by(username = g.user.username).first()
        # Return JSON using template
        return user

    @api.expect(user_request_fields)
    @api.marshal_with(user_fields, envelope='user')
    @api.doc(responses = {
        400: 'Failed to decode JSON object: Expecting value: line 1 column 1 (char 0)',
        401: 'Unauthorized access',
        404: "Can't authorize in Federal Tax Service with given phone/key",
        409: 'Username already exist',
    })
    def put(self):
        """
        Modify authorized user in database

        :return: Modified user with some data
        :rtype:  dict/json
        """
        # Parsing request JSON fields
        args = user_request.parse_args()
        # Login of authorized user stores in Flask g object
        user = User.query.filter_by(username = g.user.username).first()
        try:
            # Modify user info according to JSON fields
            for key, value in args.items():
                if value is not None:
                    if key == "password":
                        user.hash_password(value)
                        continue
                    setattr(user, key, value)
            # Error checking
            self.abortIfFtsUserDoesntExist(user.phone, user.fts_key)
            db.session.commit()
            # Return JSON using template
            return user
        except IntegrityError:
            db.session.rollback()
            abort(409, message="Username '{}' already exist".format(args['username']))

    @staticmethod
    def abortIfFtsUserDoesntExist(phone, fts_key):
        """
        Return error JSON in 409 response if user doesn't exists in Federal Tax Service

        :param username: User phone number
        :type  username: str
        :param username: SMS key
        :type  username: int
        """
        fts = FtsRequest()
        if fts.checkAuthData(phone, fts_key) is False:
            abort(404, message="Can't authorize in Federal Tax Service with given phone/key")