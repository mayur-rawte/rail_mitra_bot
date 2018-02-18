def post_facebook_message_normal(fbid, recevied_message):
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"text": recevied_message}})
    status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"}, data=response_msg)
    print(status.json())


def post_facebook_buttons(fbid, data):  # this receives a array of facebook button json
    response_msg = json.dumps({"recipient": {"id": fbid}, "message": {"attachment": {"type": "template", "payload": {
        "template_type": "button", "text": data['text'], "buttons": data['Buttons']}}}})
    # print response_msg
    status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"}, data=response_msg)
    print(status.json())

def post_running_status_reply(fbid, data):
    data = json.loads(data)
    resultData = TrainRunningStatus(data['prevData']['trainNo'], data['jStation'], data['prevData']['jDate'],
                                    data['prevData']['jDateMap'], data['prevData']['jDateDay'])
    if "err" in resultData:
        post_facebook_message_normal(fbid, resultData['err'])
        return None
    else:
        rsData = {"recipient": {"id": fbid}, "message": {"attachment": {"type": "template",
                                                                        "payload": {"template_type": "generic",
                                                                                    "elements": [{"title": resultData[
                                                                                                               'trainName'] + " is " +
                                                                                                           resultData[
                                                                                                               'delayTime'] + " Arrival : " +
                                                                                                           resultData[
                                                                                                               'actArTime'][
                                                                                                           -5:] + " Actual : " +
                                                                                                           resultData[
                                                                                                               'schArTime'][
                                                                                                           -5:],
                                                                                                  "image_url": "http://toons.artie.com/gifs/arg-newtrain-crop.gif",
                                                                                                  "subtitle":
                                                                                                      resultData[
                                                                                                          'lastLocation']}]}}}}
        status = requests.post(page_url_with_token, headers={"Content-Type": "application/json"},
                               data=json.dumps(rsData))
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
    data = {"Buttons": [{"type": "postback", "title": "Help", "payload": "help"}, {"type": "postback", "title": "Talk to me", "payload": "talk to me"} ], "text": text}
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
            print status.json()
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


# for slpliting the button array
def split(arr, size):
    arrs = []
    while len(arr) > size:
        pice = arr[:size]
        arrs.append(pice)
        arr = arr[size:]
    arrs.append(arr)
    return arrs