from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import (TimedJSONWebSignatureSerializer as Serializer, BadSignature, SignatureExpired)
from app import app, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(64), index = True, unique = True)
    password = db.Column(db.String(128))
    phone = db.Column(db.String(12))
    fts_key = db.Column(db.Integer, default = 0)

    current_table = db.relationship('Table', secondary = 'user_table')

    def hash_password(self, password):
        """
        Hash given password for store in database

        :param password: User password
        :type  password: str
        """
        self.password = generate_password_hash(password)

    def verify_password(self, password):
        """
        Match given password with hash saved in database

        :param password: User password
        :type  password: str
        :return: True if the password matched, False otherwise
        :rtype:  bool
        """
        return check_password_hash(self.password, password)

    def generate_auth_token(self, expiration = 3600):
        """
        Generate authentification bearer token with expiration by time
        from application secret key

        :param expiration: TTL of token in seconds
        :type  expiration: int
        """
        s = Serializer(app.config['SECRET_KEY'], expires_in = expiration)
        # Insert id in token
        return s.dumps({ 'id': self.id })

    @staticmethod
    def verify_auth_token(token):
        """
        Match authentification bearer token

        :param token: Bearer token
        :type  token: str
        :return: User with id inserted in token, None otherwise
        :rtype:  app.models.User/None
        """
        s = Serializer(app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        # Valid expired token
        except SignatureExpired: return None
        # Invalid token
        except BadSignature: return None
        # Check id in token
        user = User.query.get(data['id'])
        return user

    def __repr__(self):
        return '<User %r>' % (self.username)

class Table(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    table_key = db.Column(db.String(120), index = True, unique = True)
    table_info = db.Column(db.Integer, default = "")
    table_date = db.Column(db.DateTime)

    users = db.relationship('User', secondary = 'user_table')

    def __repr__(self):
        return '<Table %r>' % (self.table_key)

class Products(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    table_id = db.Column(db.Integer, db.ForeignKey(Table.id), nullable = False)
    product_name = db.Column(db.String(120), unique = True)
    count = db.Column(db.Integer)
    price = db.Column(db.Float)

    def __repr__(self):
        return '<Product %r>' % (self.product_name)

class UserTable(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable = False, unique = True, index = True)
    table_id = db.Column(db.Integer, db.ForeignKey(Table.id), nullable = False, index = True)
    price = db.Column(db.Float)

    user = db.relationship('User', backref = db.backref('user_tables', cascade="all, delete-orphan" ))
    table = db.relationship('Table', backref = db.backref('user_tables', cascade="all, delete-orphan" ))

class UserTableArchive(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable = False, index = True)
    table_id = db.Column(db.Integer, db.ForeignKey(Table.id), nullable = False, index = True)
    price = db.Column(db.Float)

class UserProduct(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey(User.id), nullable = False, index = True)
    product_id = db.Column(db.Integer, db.ForeignKey(Products.id), nullable = False, index = True)
    table_id = db.Column(db.Integer, index = True)
    count = db.Column(db.Float)
    price = db.Column(db.Float)
