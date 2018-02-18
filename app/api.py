import json

from flask import request
from flask_restful import reqparse, Resource


class RailMitraAPI(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('hub.verify_token', type=str, location='args')
        self.req_parse.add_argument('hub.challenge', type=str, location='args')

    def get(self):
        args = self.req_parse.parse_args()
        if args['hub.verify_token'] == '2318934571':
            print('verified')
            return args['hub.challenge']

    def post(self):
        data = request.get_json()
        print(data)
