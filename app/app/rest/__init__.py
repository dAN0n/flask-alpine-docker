from flask import Blueprint
from flask_restplus import Api

# Receipt-Analyzer v1.0 blueprint instance
RAv1 = Blueprint('RAv1', __name__, url_prefix='/api/v1.0')

# Type of authorizations for documentation
authorizations = {
    'basic': { 'type': 'basic' },
    'token': { 'type': 'apiKey', 'in': 'header', 'name': 'Authorization' }
}

# Blueprint REST API
api = Api(RAv1,
    authorizations = authorizations,
    security=['basic', 'token'],
    title='Receipt Analyzer',
    version='1.0',
    description="""Service for the division of products from receipts between a group of people.\n
    Note: For token authorization type "Bearer %TOKEN%" in api key authorization.""")

# Import views (must be after the blueprint object is created)
from app.rest import Auth, Token, Users, Fts

# Define namespaces in REST API (groups in documentation)
api.add_namespace(Users.api)
api.add_namespace(Fts.api)
api.add_namespace(Token.api)