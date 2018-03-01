import json

from app.facebook_functions import defaultMessage, post_facebook_message_normal, post_help_message
from app.helper import extract_data_from_api_ai


def process_train_running_status(fb_id, train_number, source_station):
    train_data = get_station_from_train_number(train_number)

def process_simple_message_request(message, fb_id):
    api_ai_result = extract_data_from_api_ai(message, fb_id)
    if 'result' in api_ai_result:
        api_ai_result = api_ai_result['result']
        if api_ai_result['metadata']['intentName'] == 'LiveStation':
            if api_ai_result['parameters']['sourceStation'] == '' or api_ai_result['parameters']['trainNumber'] == '':
                post_facebook_message_normal(fb_id, 'Something is missing ! Type \'help\' for supported commands')
            else:
                process_train_running_status(fb_id, api_ai_result['parameters']['trainNumber'],
                                             api_ai_result['parameters']['sourceStation'])


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
