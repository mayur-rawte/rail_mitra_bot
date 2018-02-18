import json
import requests
from bs4 import BeautifulSoup
import datetime
import collections
from constant import LiveStationList, TOKEN

page_url_with_token = 'https://graph.facebook.com/v2.9/me/messages?access_token=' + TOKEN

class RailMitra():
    def __init__():
        pass
    def get_running_status(train_no, journey_station, journey_date=datetime.date.today().strftime('%d-%b-%Y'),
                       journey_date_map=datetime.date.today().strftime('%d-%b-%Y'),
                       journey_date_day=str(datetime.date.today().strftime('%A')[:3]).upper()):
        data = {'trainNo': trainNo, 'jStation': jStation, 'jDate': jDate, 'jDateMap': jDate, 'jDateDay': jDateDay}
        r = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=ShowRunC', data=data)
        soup = BeautifulSoup(r.text, 'lxml')
        result_data = {}
        try:
            table = soup.find(id='ResTab')
            trs = table.find_all('tr')
            trainName = trs[0].find_all('td')[1].text
            stationName = trs[1].find_all('td')[1].text
            schArTime = trs[3].find_all('td')[1].text
            actArTime = trs[4].find_all('td')[1].text
            delayTime = trs[5].find_all('td')[1].text
            lastLocation = (trs[9].find_all('td')[1].text)
            lastLocation = " ".join(lastLocation.split())
            resultData = {'trainName': trainName, 'schArTime': schArTime, 'actArTime': actArTime, 'delayTime': delayTime,
                        'lastLocation': lastLocation, 'stationName': stationName}
        except:
            resultData['err'] = 'Either the Train Number' + str(
            trainNo) + " does\'t run on " + jDateDay + " at " + jStation[
                                                                :3] + " Station or the train number is incorrect"
        return resultData


    def get_train_meta(train_no, journey_date = datetime.date.today().strftime('%d-%b-%Y'), journey_date_day=str(datetime.date.today().strftime('%A')[:3]).upper())):
        data = data = {'trainNo': trainNo, 'jDate': jDate, 'jDateMap': jDate, 'jDateDay': jDateDay}
        r = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=FindStationList', data=data)
        soup = BeautifulSoup(r.text, 'lxml')
        stations = soup.find(id='jStation').find_all('option')[1:]
        station_list[station.get('value')] = station.text
        return json.dumps({'stations': station_list, 'original_request': data})