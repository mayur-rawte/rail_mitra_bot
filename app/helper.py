import json

import apiai

token = '5e47a85828a0400aa52a591ca95820f1'
api_ai = apiai.ApiAI(token)


def extract_data_from_api_ai(text, fb_id):
    ai_request = api_ai.text_request()
    ai_request.session_id = fb_id
    ai_request.query = text
    ai_response = ai_request.getresponse()
    return json.loads(ai_response.read())


# for slpliting the button array
def split(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs
