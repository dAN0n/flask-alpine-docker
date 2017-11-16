from flask import g
from flask_restplus import Namespace, Resource, fields
from app.models import User
from app.rest.Auth import Auth

# Define namespace
api = Namespace('Token', description='Recieve JWS token', path='/')

### JSON Models ###

# Response JSON template
token_fields = api.model('Token response',
{
    'token': fields.String(description='Bearer token', required = True),
})

@api.route('/token', endpoint = 'token')
class Token(Resource):
    """
    Obtaining bearer token for authorized user

    :var     method_decorators: Decorators applied to methods
    :vartype method_decorators: list
    """
    method_decorators = [Auth.basic_auth.login_required]

    @api.doc(security = [ 'basic' ])
    @api.marshal_with(token_fields)
    @api.response(401, 'Unauthorized access')
    def get(self):
        """
        Obtaining bearer token for authorized user

        :return: bearer token for authorized user
        :rtype:  dict/json
        """
        # Login of authorized user stores in Flask g object
        user = User.query.filter_by(username = g.user.username).first()
        # Generate token
        token = user.generate_auth_token()
        # Send token in ASCII format
        return { 'token': token.decode('ascii') }