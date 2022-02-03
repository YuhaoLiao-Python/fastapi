import json
import os
from linebot.models import FlexSendMessage
from models.message_request import MessageRequest
from skills import add_skill
import requests

weatheritem = '''{
  "type": "bubble",
  "size": "kilo",
  "body": {
    "type": "box",
    "layout": "vertical",
    "contents": [
      {
        "type": "text",
        "text": "臺北市 - 稍有寒意至舒適",
        "weight": "bold",
        "size": "sm",
        "wrap": true
      },
      {
        "type": "text",
        "text": "10/05 18:00 ~ 10/06 06:00",
        "weight": "bold",
        "size": "sm",
        "wrap": true
      },
      {
        "type": "box",
        "layout": "baseline",
        "contents": [
          {
            "type": "text",
            "text": "降雨機率 30%",
            "size": "xs",
            "color": "#8c8c8c",
            "flex": 0
          }
        ]
      },
      {
        "type": "box",
        "layout": "vertical",
        "contents": [
          {
            "type": "box",
            "layout": "baseline",
            "spacing": "sm",
            "contents": [
              {
                "type": "text",
                "wrap": true,
                "color": "#8c8c8c",
                "size": "xs",
                "flex": 5,
                "text": "氣溫 26°C~29°C"
              }
            ]
          }
        ]
      }
    ],
    "spacing": "sm",
    "paddingAll": "13px"
  }
}'''

weather = '''{
    "type": "carousel",
    "contents": [
    ]
}'''

@add_skill('/天氣')
def get(message_request: MessageRequest):

    # /天氣預報 臺北市
    city = message_request.message.split()[1]

    # 串接 openAPI
    code = 'CWB-4DDCEDEF-C8BA-4598-B09A-8CD1BE31241B'
    url = f"https://opendata.cwb.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization={code}&format=JSON&locationName={city}"
    payload = {}
    headers = {
        'accept': 'application/json',
        'Cookie': 'TS01dbf791=0107dddfefba206e5b7f0c1ed580514ff49ac420ad0102f08071800ff1e5302948e45793cd45931b688552680395d734c467db30fe'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    data = response.json()

    # 處理回傳的JSON
    location = list(data['records']['location'])
    elements = location[0]['weatherElement']
    
    # 舒適度
    ci = list(filter(lambda c: c['elementName'] == 'CI', elements))[0]
    # 降雨機率
    pop = list(filter(lambda c: c['elementName'] == 'PoP', elements))[0]
    # 最低溫度
    minT = list(filter(lambda c: c['elementName'] == 'MinT', elements))[0]
    # 最高溫度
    maxT = list(filter(lambda c: c['elementName'] == 'MaxT', elements))[0]

    # 美化回傳字串
    flex = json.loads('weather.json')
     
    for i in range(3): 
        item = json.loads(weatheritem)
        
        item['body']['contents'][0]['text'] = f"{city} - {ci['time'][i]['parameter']['parameterName']}"
        item['body']['contents'][1]['text'] = f"{ci['time'][i]['startTime']} ~ {ci['time'][i]['endTime']}"
        item['body']['contents'][2]['contents'][0]['text'] = f"降雨機率 {pop['time'][i]['parameter']['parameterName']}%"
        min = minT['time'][i]['parameter']['parameterName'] + '°C'
        max = maxT['time'][i]['parameter']['parameterName'] + '°C'
        item['body']['contents'][3]['contents'][0]['contents'][0]['text'] = f"{min} ~ {max}"
        flex['contents'].append(item)
     
    
    msg = FlexSendMessage(alt_text='天氣預報', contents=flex)

    return [
        msg
    ]
