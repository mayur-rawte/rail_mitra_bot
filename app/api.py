import json
from flask import request
from flask_restful import reqparse, Resource
from app import facebook_functions, rail_api

from app.helper import extract_data_from_api_ai
from app.rail_api import RailMitra


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
                        api_ai_result = extract_data_from_api_ai(message['message']['text'], fb_id)
                        self.process_api_ai_result(api_ai_result['result'], fb_id)
                except Exception as e:
                    print('exception ')
                    print(e)

    def process_api_ai_result(self, api_ai_result, fb_id):
        print(json.dumps(api_ai_result, indent=4))
        if 'metadata' in api_ai_result:
            if api_ai_result['metadata']['intentName'] == 'TrainStatus':
                if api_ai_result['parameters']['sourceStation'] == '' or api_ai_result['parameters']['DestinationStation'] == '':
                    facebook_functions.post_facebook_message_missing_params(fb_id)
                else:
                    rail_mitra = RailMitra().get_running_status()
            elif api_ai_result['metadata']['intentName']:
                if 'fulfillment' in api_ai_result:
                    facebook_functions.post_facebook_message_normal(fb_id, api_ai_result['fulfillment']['speech'])
                else:
                    print('error')
        else:
            print('no neta')
