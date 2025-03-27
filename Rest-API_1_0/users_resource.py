from flask import abort, jsonify, make_response, Flask
from werkzeug.security import check_password_hash, generate_password_hash
from flask_restful import reqparse, abort, Api, Resource
from data import db_session
import datetime
from data.reqparse_user import parser
from data.users import User


def check_password(self, password):
    return check_password_hash(self.hashed_password, password)
    

def set_password(password):
    return generate_password_hash(password)


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    if not user_id.isdigit():
        abort(404, message=f"{user_id} is not integer")
    else:
        user_id = int(user_id)
        users = session.query(User).get(user_id)
        if not users:
            abort(404, message=f"User {user_id} not found")


class UsersResource(Resource, User):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        users = session.query(User).get(user_id)
        return jsonify({'users': users.to_dict(only=('name', 'surname', 'age', 'address',
                                                     'email', 'position', 'speciality',
                                                     'hashed_password'))})
    
    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()    
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(only=('name', 'surname', 'age', 'address',
                                                     'email', 'position', 'speciality',
                                                     'hashed_password')) for item in users]})
    
    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()
        user = User(
            name=args['name'],
            surname=args['surname'],
            age=args['age'],
            address=args['address'],
            email=args['email'],
            position=args['position'],
            speciality=args['speciality'],
            hashed_password=set_password(args['hashed_password'])
        )
        session.add(user)
        session.commit()
        return jsonify({'id': user.id})