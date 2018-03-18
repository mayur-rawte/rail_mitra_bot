import json

from app import facebook_functions
from app.facebook_functions import defaultMessage, post_facebook_message_normal, post_help_message, \
    post_facebook_buttons, post_facebook_train_status_response
from app.helper import extract_data_from_api_ai
from app.rail_api import RailMitra

rail_mitra = RailMitra()


def process_train_running_status(fb_id, train_number, source_station):
    station_list = json.loads(rail_mitra.get_stations_from_train_number(train_number))
    button_list = []
    for k, v in station_list['stations'].items():
        if source_station.lower() in v.lower():
            payload = json.dumps({"jStation": k, "prevData": station_list['originalReq']})
            button_list.append({"type": "postback", "title": v, "payload": payload})
    # [pps(k, v) for k, v in station_list['stations'].iteritems() if source_station.lower() in v.lower()]
    if not button_list:
        post_facebook_message_normal(fb_id,
                                     "We did not find any related station with this train. Did you spell it correctly. Please try again ")
    else:
        payload_data = json.loads(button_list[0]['payload'])
        print(payload_data)
        print(type(payload_data))
        result_data = rail_mitra.get_running_status(payload_data['prevData']['trainNo'], payload_data['jStation'],
                                                    payload_data['prevData']['jDate'],
                                                    payload_data['prevData']['jDateMap'],
                                                    payload_data['prevData']['jDateDay'])
        post_facebook_train_status_response(fb_id, result_data)


def process_simple_message_request(message, fb_id):
    api_ai_result = extract_data_from_api_ai(message, fb_id)
    if 'result' in api_ai_result:
        api_ai_result = api_ai_result['result']
        print(api_ai_result)
        if api_ai_result['metadata'] and api_ai_result['metadata']['intentName'] == 'TrainStatus':
            if api_ai_result['parameters']['sourceStation'] == '' or api_ai_result['parameters'][
                'trainNumber'] == '':
                post_facebook_message_normal(fb_id, 'Something is missing ! Type \'help\' for supported commands')
            else:
                process_train_running_status(fb_id, api_ai_result['parameters']['trainNumber'],
                                             api_ai_result['parameters']['sourceStation'])
        elif api_ai_result['fulfillment'] and api_ai_result['fulfillment']['speech']:
            print('inside elif')
            post_facebook_message_normal(fb_id, api_ai_result['fulfillment']['speech'])
        else:
            print('nai')


def process_postback_message_request(message, fb_id):
    if message.lower() == 'help':
        post_help_message(fb_id)
    elif message.lower() == 'hi':
        defaultMessage(fb_id)
    elif message.lower() == 'talk to me':
        talk_to_me_text = 'You can start asking me \n Who are you? \n Who is your boss? \n you are fired ? \n You are bad \n What\'s your birth date? \n are you busy? \n can you help me? \n you are good. \n are you happy? \n do you have a hobby? \n are you hungy? \n are we friends? \n where do you live? \n For more commands reply with More'
        post_facebook_message_normal(talk_to_me_text, fb_id)
    else:
        postback_data = json.loads(message)
        if 'validStationFrom' in postback_data and not 'validStationTo' in postback_data:
            pass


def process_api_ai_result(self, api_ai_result, fb_id):
    print(json.dumps(api_ai_result, indent=4))
    if 'metadata' in api_ai_result:
        if api_ai_result['metadata']['intentName'] == 'TrainStatus':
            if api_ai_result['parameters']['sourceStation'] == '' or api_ai_result['parameters'][
                'trainNumber'] == '':
                facebook_functions.post_facebook_message_missing_params(fb_id)
            else:
                rail_mitra.get_running_status(api_ai_result['parameters']['trainNumber'],
                                              api_ai_result['parameters']['sourceStation'])
        elif api_ai_result['metadata']['intentName']:
            if 'fulfillment' in api_ai_result:
                facebook_functions.post_facebook_message_normal(fb_id, api_ai_result['fulfillment']['speech'])
            else:
                print('error')
    else:
        print('no neta')
