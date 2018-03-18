import json
import requests
from bs4 import BeautifulSoup
import datetime
import collections

from app.contant import TOKEN

page_url_with_token = 'https://graph.facebook.com/v2.9/me/messages?access_token=' + TOKEN


class RailMitra:
    def __init__(self):
        pass

    @staticmethod
    def get_running_status(train_no, journey_station, journey_date=datetime.date.today().strftime('%d-%b-%Y'),
                           journey_date_map=datetime.date.today().strftime('%d-%b-%Y'),
                           journey_date_day=str(datetime.date.today().strftime('%A')[:3]).upper()):
        request_data = {'trainNo': train_no,
                        'jStation': journey_station,
                        'jDate': journey_date,
                        'jDateMap': journey_date_map,
                        'jDateDay': journey_date_day
                        }
        response = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=ShowRunC',
                                 data=request_data)
        soup = BeautifulSoup(response.text, 'lxml')
        result_data = {}
        try:
            table = soup.find(id='ResTab')
            trs = table.find_all('tr')
            result_data['trainName'] = trs[0].find_all('td')[1].text
            result_data['stationName'] = trs[1].find_all('td')[1].text
            result_data['schArTime'] = trs[3].find_all('td')[1].text
            result_data['actArTime'] = trs[4].find_all('td')[1].text
            result_data['delayTime'] = trs[5].find_all('td')[1].text
            result_data['lastLocation'] = " ".join(trs[9].find_all('td')[1].text.split())
        except Exception as e:
            print(e)
            result_data['err'] = 'Either the Train Number'
            result_data['err'] += str(train_no)
            result_data['err'] += " does\'t run on "
            result_data['err'] += journey_date_day
            result_data['err'] += " at "
            result_data['err'] += journey_station[:3]
            result_data['err'] += " Station or the train number is incorrect"
        return result_data

    @staticmethod
    def get_stations_from_train_number(train_no, journey_date=datetime.date.today().strftime('%d-%b-%Y'), journey_date_day=str(datetime.date.today().strftime('%A')[:3]).upper()):
        request_data = {'trainNo': train_no, 'jDate': journey_date, 'jDateMap': journey_date, 'jDateDay': journey_date_day}
        station_list = collections.OrderedDict()
        response = requests.post('https://enquiry.indianrail.gov.in/mntes/q?opt=TrainRunning&subOpt=FindStationList', data=request_data)
        soup = BeautifulSoup(response.text, 'lxml')
        stations = soup.find(id='jStation').find_all('option')[1:]
        for station in stations:
            station_list[station.get('value')] = station.text
        final_data = {'stations': station_list, 'originalReq': request_data}
        return json.dumps(final_data)
