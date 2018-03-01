import json
from flask import request
from flask_restful import reqparse, Resource
from app import facebook_functions, rail_api

from app.helper import extract_data_from_api_ai
from app.main_function import process_simple_message_request, process_postback_message_request
from app.rail_api import RailMitra

rail_mitra = RailMitra()


class RailMitraAPI(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('hub.verify_token', type=str, location='args')
        self.req_parse.add_argument('hub.challenge', type=str, location='args')

    def get(self):
        args = self.req_parse.parse_args()
        if args['hub.verify_token'] == '2318934571':
            return_challenge = args['hub.challenge']
            return int(return_challenge)

    def post(self):
        data = request.get_json()
        for entry in data['entry']:
            for message in entry['messaging']:
                fb_id = message['sender']['id']
                try:
                    if 'message' in message:
                        process_simple_message_request(message['message']['text'], fb_id)
                    elif 'postback' in message:
                        process_postback_message_request(message['postback']['payload'], fb_id)
                except Exception as e:
                    print('exception')
                    print(e)


