import json
from flask import request
from flask_restful import reqparse, Resource
from app import facebook_functions

from app.helper import extract_data_from_api_ai


class RailMitraAPI(Resource):
    def __init__(self):
        self.req_parse = reqparse.RequestParser()
        self.req_parse.add_argument('hub.verify_token', type=str, location='args')
        self.req_parse.add_argument('hub.challenge', type=str, location='args')

    def get(self):
        args = self.req_parse.parse_args()
        if args['hub.verify_token'] == '2318934571':
            print('verified')
            return args['hub.challenge'].replace("\"", '').replace('\'', '').replace("\n", '')

    def post(self):
        data = request.get_json()
        for entry in data['entry']:
            for message in entry['messaging']:
                fb_id = message['sender']['id']
                if 'message' in message:
                    api_ai_text = extract_data_from_api_ai(message['message']['text'], fb_id)
                    if api_ai_text['result']['metadata']['intentName'] == 'LiveStation':
                        if api_ai_text['result']['parameters']['sourceStation'] == '' or \
                                api_ai_text['result']['parameters']['DestinationStation'] == '':
                            facebook_functions.post_facebook_message_normal(fb_id,
                                                                            'Something is missing ! Type \'help\' for '
                                                                            'supported commands')
                    else:
                        facebook_functions.post_facebook_message_normal(fb_id, 'Hello there!')
