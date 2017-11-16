from flask import g, request
from flask_restplus import Namespace, Resource, fields, abort
from app.models import User
from app.FtsRequest import FtsRequest
from app.rest.Auth import Auth

# Define namespace
api = Namespace('FTS', description='Requests to Federal Tax Service', path='/')

### JSON Parsers ###

# FTS users request JSON fields
fts_user_request = api.parser()
fts_user_request.add_argument('name', type = str, required = True,
    help = 'No name provided', location = 'json')
fts_user_request.add_argument('email', type = str, required = True,
    help = 'No email provided', location = 'json')
fts_user_request.add_argument('phone', type = str, required = True,
    help = 'No phone provided', location = 'json')

# Receipt request JSON fields
receipt_request = api.parser()
receipt_request.add_argument('fn', type = int, required = True,
    help = 'No fn provided', location = 'args')
receipt_request.add_argument('fd', type = int, required = True,
    help = 'No fd provided', location = 'args')
receipt_request.add_argument('fp', type = int, required = True,
    help = 'No fp provided', location = 'args')

### JSON Models ###

# Registration in FTS request JSON fields
fts_user_request_fields = api.model('FTS users request',
{
    'name': fields.String(description='Login', required=True),
    'email': fields.String(description='Email', required=True),
    'phone': fields.String(description='Phone number', required=True),
})

# Check if user exists in Federal Tax Service JSON response
check_fields = api.model('FTS existence check',
{
    'check': fields.Boolean(description='User existing in FTS', required = True),
})

# JSON response with message
message_fields = api.model('FTS Message response',
{
    'message': fields.String(description='Message', required = True),
})

# Part of items_fields
one_item_fields = api.model('Item response',
{
    'name': fields.String(description='Product name', required=True),
    'quantity': fields.Integer(description='Quantity', required=True),
    'price': fields.Integer(description='Price', required=True),
})

# Products response JSON fields
items_fields = api.model('Products response',
{
    'items': fields.List(fields.Nested(one_item_fields)),
})

@api.route('/fts/users', endpoint = 'fts_users')
class FtsSignUp(Resource):
    """
    Register new user in Federal Tax Service
    """
    @api.doc(security = [ 'basic' ])
    @api.marshal_with(check_fields)
    @api.doc(responses = {
        400: 'The resource requires the Basic authentication',
        404: 'check: false',
    })
    def get(self):
        """
        Check if user exists in Federal Tax Service
        Phone and SMS key send as Basic Auth header

        :return: JSON with "check" field True if user exists, False otherwise
        :rtype:  dict/json
        """
        # Check if authorization is Basic Auth
        if request.authorization is None:
            abort(400, message="The resource requires the Basic authentication")
        # Get phone and SMS key from Basic Auth header
        phone = request.authorization.username
        fts_key = request.authorization.password
        # Send check auth request
        fts = FtsRequest()
        auth = fts.checkAuthData(phone, fts_key)
        # Return JSON
        result = { 'check': auth }
        return (result, 200) if auth else (result, 404)

    @api.doc(security = None)
    @api.expect(fts_user_request_fields)
    @api.marshal_with(message_fields)
    @api.response(400, """No name/email/phone provided
        [“Missing required property: phone”]
        [“String is too long (35 chars), maximum 19”]
        [“String does not match pattern ^\+\d+$: ghg”]
        [“Object didn’t pass validation for format email: tt”]""")
    def post(self):
        """
        Create new user in Federal Tax Service and send password SMS

        :return: Response message
        :rtype:  dict/json
        """
        # Parsing request JSON fields
        args = fts_user_request.parse_args()
        # Send signup request
        fts = FtsRequest()
        request = fts.signUp(args['name'], args['email'], args['phone'])
        # Restore password if user exists
        if request['ftsRequestSuccess'] is False and request['error'] == "user exists":
            fts.restorePassword(args['phone'])
        # Send error JSON if bad request
        if request['ftsRequestSuccess'] is False and request['error'] != "user exists":
            abort(request['responseCode'], message = request['error'])
        # Return JSON
        return { 'message': 'SMS with password was sent to {}'.format(args['phone'])}, 200

@api.route('/fts/receipts', endpoint = 'fts_receipts')
class FtsReceiptRequest(Resource):
    """
    Operations with FTS receipts

    :var     method_decorators: Decorators applied to methods
    :vartype method_decorators: list
    """
    method_decorators = [Auth.multi_auth.login_required]

    @api.marshal_with(items_fields, envelope='items')
    @api.param('fp', 'ФП number', required = True)
    @api.param('fd', 'ФД number', required = True)
    @api.param('fn', 'ФН number', required = True)
    @api.doc(responses = {
        400: 'No fn/fd/fp provided',
        401: 'Unauthorized access',
        403: 'the user was not found or the specified password was not correct',
        406: 'the ticket was not found',
        408: 'Empty JSON response',
    })
    def get(self):
        """
        Get receipt with given ФН, ФД and ФП numbers
        ФН, ФД and ФП numbers getting from fn, fd and fp query parameters

        :return: Products from receipt with name, quantity and price of 1 piece of product
        :rtype:  dict/json
        """
        # Parsing request JSON fields
        args = receipt_request.parse_args()
        # Login of authorized user stores in Flask g object
        user = User.query.filter_by(username = g.user.username).first()
        # Send request of receipt JSON
        fts = FtsRequest()
        request = fts.getReceipt(args['fn'], args['fd'], args['fp'], user.phone, user.fts_key)
        # Send error JSON if bad request
        if request['ftsRequestSuccess'] is False:
            abort(request['responseCode'], message = request['error'])
        # Extract products info from JSON
        result = {}
        result['items'] = [ {
            'name': item['name'],
            'quantity': item['quantity'] if isinstance(item['quantity'], int) else 1,
            'price': item['price'] if isinstance(item['quantity'], int) else item['sum']
            } for item in request['items'] ]
        # Return extracted part of JSON
        return result, 200