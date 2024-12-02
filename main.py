import json
import sys, os
import urllib3
import pandas as pd
import schedule
import time
from line_notify import LineNotify

from secret_keys import *
from utils import *


class JMA_Earthquake():
    def __init__(self):
        self.index = 0
        self.lang = 'kr'
        self.current_dir = os.path.dirname(os.path.realpath(__file__))
        self.json_file_path = os.path.join(self.current_dir, 'json_file.json')
        self.urllib = urllib3.PoolManager()
        
    def load_json(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        
        return data


    def save_json(self, file_path, data):
        with open(file_path, 'w') as fp:
            json.dump(data, fp, ensure_ascii=False, indent=4)


    def load_API_data(self):
        url = f"https://www.jma.go.jp/bosai/quake/data/list.json"
        
        response = self.urllib.request(method='GET', url=url, headers=None).json()
        jma_data = response[0]
        
        previous_data = self.load_json(self.json_file_path)
        if (jma_data['eid'] == previous_data['eid']) and (jma_data['anm'] == previous_data['anm']):
            return None
        else:
            self.save_json(file_path=self.json_file_path, data=jma_data)
            dataDict = self.process_data(jma_data)
            
            return dataDict
        
    def process_data(self, jma_data):
        '''
        eid: 지진 탐지 시각
        ctt: 지진 발표 시각
        cod: 위도, 경도, 깊이
        ttl: 정보 타입
        en_ttl: 정보 타입 - 영문명
        anm: 진앙 지역
        en_anm: 진앙 지역 - 영문명
        mag: 매드니튜드
        maxi: 진도
        '''
        
        eid = jma_data.get('eid', '')
        ctt = jma_data.get('ctt', '')
        cod = jma_data.get('cod', '')
        ttl = jma_data.get('ttl', 'Unknown')
        en_ttl = jma_data.get('en_ttl', 'Unknown')
        anm = jma_data.get('anm', 'Unknown')
        en_anm = jma_data.get('en_anm', 'Unknown')
        mag = jma_data.get('mag', 'N/A')
        maxi = jma_data.get('maxi', [])

        eid_convert = convert_datetime(eid)
        if not cod:
            latitude, longitude, depths = (0, 0, [0])
        else:
            coordinates = [parse_coordinates(cod)]
            latitude, longitude, depths = zip(*coordinates) 
        
        latitude = str(latitude[0])
        longitude = str(longitude[0])
        depths = [-0.001 * depth for depth in depths]
        
        jma_url = f"https://www.jma.go.jp/jma/index.html"
        map_url = f"https://www.jma.go.jp/bosai/map.html#lang={self.lang}&elem=int&contents=earthquake_map&area_type=japan&id={eid}"
        inform_url = f"https://www.data.jma.go.jp/multi/quake/quake_detail.html?eventID={ctt}&lang={self.lang}"
        maxi_url = f"https://www.data.jma.go.jp/multi/quake/quake_advisory.html?lang={self.lang}"

        dataDict = {}
        dataDict['ttl'] = ttl
        dataDict['en_ttl'] = en_ttl
        dataDict['eid_convert'] = str(eid_convert)
        dataDict['anm'] = anm
        dataDict['en_anm'] = en_anm
        dataDict['mag'] = mag
        dataDict['maxi'] = maxi
        dataDict['Latitude'] = latitude
        dataDict['Longitude'] = longitude
        dataDict['jma_depths'] = depths
        dataDict['jma_url'] = jma_url
        dataDict['map_url'] = map_url
        dataDict['inform_url'] = inform_url
        dataDict['maxi_url'] = maxi_url
        
        return dataDict
        

def get_Line_Token():
    BASE_DIR = os.path.dirname(os.path.realpath(__file__))
    secret_file = os.path.join(BASE_DIR, 'secret_keys.json')
    ACCESS_TOKEN = GET_SECRET_KEYS(file_path=secret_file, tag_name="SECRET_KEY")
    
    return ACCESS_TOKEN


def set_JP_Message(dataDict):
    message = f"""

[ {dataDict['ttl']} ]

■ 발생 시각: {dataDict['eid_convert']}
■ 발생 위치: {dataDict['anm']}
■ 규모: {dataDict['mag']}
■ 최대 진도: {dataDict['maxi']}
■ 위도: {dataDict['Latitude']}, 경도: {dataDict['Longitude']}
■ 진앙지:
{dataDict['map_url']}
■ 기상청 진도 정보:
{dataDict['inform_url']}

▸ 정보 제공: 일본 기상청 (JMA)
"""
    
    return message


def send_Line_Message(dataDict):
    ACCESS_TOKEN = get_Line_Token()
    print(f'ACCESS_TOKEN: {ACCESS_TOKEN}')
    notify = LineNotify(ACCESS_TOKEN)
    
    jp_msg = set_JP_Message(dataDict=dataDict)
    print(jp_msg)
    notify.send(jp_msg)
    

# Function to retrieve data periodically
def job():
    jma = JMA_Earthquake()
    dataDict = jma.load_API_data()
    
    if dataDict is not None:
        send_Line_Message(dataDict=dataDict)
    else:
        print('PASS')
        pass

# Run the task at the top of every minute (ex: 12:00:00, 12:01:00, ...)
schedule.every().minute.at(":00").do(job)


# Execute tasks periodically in an infinite loop
if __name__ == "__main__":
    while True:
        # Run scheduled tasks
        schedule.run_pending()
        # Wait every second
        time.sleep(1)

