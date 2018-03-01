import json
import requests
from bs4 import BeautifulSoup

from app.rail_api import RailMitra
from function import page_url_with_token

headers = {'Content-Type': 'application/json'}


def prepare_message(fb_id, message_type, data):
    prepared_message = {'recipient': {'id': fb_id}}
    if message_type == 'text':
        prepared_message['message'] = {'text': data}
    elif message_type == 'buttons':
        prepared_message['message'] = {'attachment': {'type': 'template',
                                                      'payload':
                                                          {'template_type': 'button',
                                                           'text': data['text'],
                                                           'buttons': data['Buttons']
                                                           }
                                                      }
                                       }
    elif message_type == 'template':
        result_title = data['trainName']
        result_title += 'is'
        result_title += data['delayTime']
        result_title += ' Arrival '
        result_title += data['actArTime'][-5:]
        result_title += " Actual: "
        result_title += data['schArTime'][-5:]
        result_title += data['actArTime']
        prepared_message['message'] = {"attachment": {"type": "template",
                                                      "payload":
                                                          {"template_type": "generic",
                                                           "elements":
                                                               [
                                                                   {"title": result_title,
                                                                    "image_url": "http://toons.artie.com/gifs/arg-newtrain-crop.gif",
                                                                    "subtitle": data['lastLocation']
                                                                    }
                                                               ]
                                                           }
                                                      }
                                       }
    print(prepared_message)
    return json.dumps(prepared_message)


def post_facebook_message_normal(fb_id, recevied_message):
    response_msg = prepare_message(fb_id, 'text', recevied_message)
    status = requests.post(page_url_with_token, headers=headers, data=response_msg)
    print(status.json())


def post_facebook_buttons(fbid, data):  # this receives a array of facebook button json
    response_msg = prepare_message(fbid, 'buttons', data)
    # print response_msg
    status = requests.post(page_url_with_token, headers=headers, data=response_msg)
    print(status.json())


def post_facebook_message_missing_params(fb_id):
    response_msg = prepare_message(fb_id, 'text', 'Something is missing ! Type \'help\' for supported commands')
    status = requests.post(page_url_with_token, headers=headers, data=response_msg)
    print(status.json())


def post_station_options_for_live_status(fb_id, train_no, station):
    rail_mitra = RailMitra()
    station_list_data = rail_mitra.get_stations_from_train_number(train_no)
    button_list = []

    def pps(k, v):
        payload = json.dumps({"jStation": k, "prevData": station_list_data['originalReq']})
        button_list.append({"type": "postback", "title": v, "payload": payload})

    [pps(k, v) for k, v in station_list_data['stations'].iteritems() if station.lower() in v.lower()]
    if not button_list:
        post_facebook_message_normal(fb_id,
                                     'We did not find any related station with this train. Did you spell it correctly. Please try again ')
    else:
        post_running_status_reply(fb_id, button_list[0]['payload'])


def post_running_status_reply(fb_id, data):
    data = json.loads(data)
    rail_mitra = RailMitra()
    result_data = rail_mitra.get_running_status(data['prevData']['trainNo'],
                                                data['jStation'],
                                                data['prevData']['jDate'],
                                                data['prevData']['jDateMap'],
                                                data['prevData']['jDateDay'])
    if "err" in result_data:
        post_facebook_message_normal(fb_id, result_data['err'])
        return None
    else:
        request_data = prepare_message(fb_id, 'template', result_data)
        status = requests.post(page_url_with_token, headers=headers, data=json.dumps(request_data))
        print(status.json())


def post_generic_template(data):
    # rsData = {"recipient": {"id": fbid }, "message": {"attachment": {"type": "template", "payload": {"template_type": "generic", "elements": [{"title": resultData['trainName'] + " is "+ resultData['delayTime'] +" Arrival : "+ resultData['actArTime'][-5:] +" Actual : "+ resultData['schArTime'][-5:], "image_url": "http://toons.artie.com/gifs/arg-newtrain-crop.gif", "subtitle": resultData['lastLocation'] } ] } } } }
    status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    print(status.json())


def defaultMessage(fbid):
    NormalMessage = "Hi! I am RailMitra. I help people to get there required train information."
    post_facebook_message_normal(fbid, NormalMessage)
    rsData = {"recipient": {"id": fbid}, "message": {"attachment": {"type": "template",
                                                                    "payload": {"template_type": "generic",
                                                                                "elements": [{
                                                                                    "title": "Simran Could have missed her train. Coz She did't ask RailMitra",
                                                                                    "image_url": "http://static.dnaindia.com/sites/default/files/2014/11/29/288247-ddlj-1.jpg",
                                                                                    "subtitle": "Simran Was not Smart but you are !"}]}}}}
    post_generic_template(rsData)
    text = "For more information Reply with 'help' or click buttons below"
    data = {"Buttons": [{"type": "postback", "title": "Help", "payload": "help"},
                        {"type": "postback", "title": "Talk to me", "payload": "talk to me"}], "text": text}
    post_facebook_buttons(fbid, data)


def getLiveStation(fbid, stationFrom, stationTo):
    url = 'https://enquiry.indianrail.gov.in/mntes/q?opt=LiveStation&subOpt=show'
    data = 'jFromStationInput=' + stationFrom + '&jToStationInput=' + stationTo + '&nHr=4&jStnName=&jStation='
    r = requests.post(url, headers={"Content-Type": "application/x-www-form-urlencoded"}, data=data)
    soup = BeautifulSoup(r.text, 'lxml')
    try:
        trs = soup.find('tbody').find_all('tr')
        post_facebook_message_normal(fbid, "There are " + str(
            len(trs) - 2) + " trains in next 4 hours between " + stationFrom + " and " + stationTo)
        for i in range(2, len(trs)):
            trainName = trs[i].find_all('td')[0].text
            trainArr, trainDep = (trs[i].find_all('td')[1].text).split()
            atrainArr, atrainDep = (trs[i].find_all('td')[2].text).split()
            platform = trs[i].find_all('td')[3].text
            rsData = {"recipient": {"id": fbid}, "message": {"attachment": {"type": "template",
                                                                            "payload": {"template_type": "generic",
                                                                                        "elements": [{
                                                                                            "title": trainName + " will Arrive at " + atrainArr + " on platform number " + platform,
                                                                                            "image_url": "",
                                                                                            "subtitle": "Sample"}]}}}}
            status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"},
                                   data=json.dumps(rsData))
            print(status.json())
    except:
        try:
            err = soup.find_all(class_='errorTextL11')[0]
            post_facebook_message_normal(fbid, err.text)
        except:
            post_facebook_message_normal(fbid, "Server Error please try after some time")


def sendAttachment(fbid, data):
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": data})
    status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"}, data=response_msg)
    print(status.json())


def post_help_message(fb_id):
    response_message = {
        "recipient": {"id": fb_id},
        "message":
            {"attachment":
                 {"type": "template",
                  "payload": {"template_type": "generic",
                              "elements": [
                                  {"title": "I am here to help you !",
                                   "image_url": "https://s-media-cache-ak0.pinimg.com/736x/1a/22/8a/1a228a1d771c36dbe7b301a5a1d608fa--cv-writing-service-writing-services.jpg",
                                   "subtitle": "Below are some queries you can ask me"
                                   }
                              ]
                              }
                  }
             }
    }
    post_generic_template(response_message)

    # rsData = {"recipient": {"id": fbid}, "message": {"attachment": {"type": "template",
    #                                                               "payload": {"template_type": "generic",
    #                                                                           "elements": [{
    #                                                                                            "title": "FromStation <space> to <space> ToStation , Example : Bhopal to Burhanpur",
    ##                                                                                            "image_url": "https://ci.memecdn.com/9785823.jpg",
    #                                                                                           "subtitle": "For Train between these station in next 4 hours"}]}}}}
    # railapi.post_generic_template(rsData)
    post_facebook_message_normal(fb_id,
                                 "For Running train status you can ask \n\nFind status for 11057 at bhopal \n\nGet me live status for 11057 at Bhopal \n\nI am at Bhopal station waiting for 11057 ")
    post_facebook_message_normal(fb_id,
                                 "For Trains between status within next 4 hours \n\nLive station for bhopal to goa \n\nTrain between Bhopal to goa \n\nBhopal to goa or as you wish to ask me")
