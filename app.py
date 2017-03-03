#!/usr/bin/env python

import urllib
import json
import os

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

def sendFCM():
    url = 'https://fcm.googleapis.com/fcm/send'
    body = {
        "data":{
            "title":"mytitle",
            "body":"mybody"
        },
        "to": "efes7pJltPE:APA91bEztbMyGUmu_KlvrTXkI3zBGql7UVm1MmKtyaFVDwzPD8GC3VUELFxJva31b1824EcUvdwijPSw_wwMXRdkkoeHJW8RyvDojIN7JPktuirUQtumffxAoHTz1-qSqYXPCWpKKrT5"
    }
    headers = {"Content-Type":"application/json", "Authorization":"key=AAAA2PBQuWc:APA91bGzMKACFHqoiXpAzO88WmwZWqQcZz5N43Zfmzb-DV0nKKzYvCMdDHc1qmTb7yucMBnq5P9_-L9z2_MwtLC63kMY-AEaiXh-TaUWKYBmbKsO0dXAqj26eCnu0JGbSrOEXC0J1Nd9"}
    r = requests.post(url, data=json.dumps(body), headers=headers)
    print("sendFCM result:")
    print(r)
    return r

@app.route('/webhook', methods=['POST'])
def webhook():
    sendFCM()
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    #res = processRequest(req)
	speech = "This is the first weather app response for seoul"
	res = {
        "speech": speech,
        "displayText": speech,
        # "data": data,
        # "contextOut": [],
        "source": "mytestweatherapp"
    }
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def processRequest(req):
    if req.get("result").get("action") != "yahooWeatherForecast":
        return {}
    baseurl = "https://query.yahooapis.com/v1/public/yql?"
    yql_query = makeYqlQuery(req)
    if yql_query is None:
        return {}
    yql_url = baseurl + urllib.urlencode({'q': yql_query}) + "&format=json"
    print(yql_url)

    result = urllib.urlopen(yql_url).read()
    print("yql result: ")
    print(result)

    data = json.loads(result)
    res = makeWebhookResult(data)
    return res


def makeYqlQuery(req):
    result = req.get("result")
    parameters = result.get("parameters")
    city = parameters.get("geo-city")
    if city is None:
        return None

    return "select * from weather.forecast where woeid in (select woeid from geo.places(1) where text='" + city + "')"


def makeWebhookResult(data):
    query = data.get('query')
    if query is None:
        return {}

    result = query.get('results')
    if result is None:
        return {}

    channel = result.get('channel')
    if channel is None:
        return {}

    item = channel.get('item')
    location = channel.get('location')
    units = channel.get('units')
    if (location is None) or (item is None) or (units is None):
        return {}

    condition = item.get('condition')
    if condition is None:
        return {}

    # print(json.dumps(item, indent=4))

    #speech = "Today in " + location.get('city') + ": " + condition.get('text') + \
    #         ", the temperature is " + condition.get('temp') + " " + units.get('temperature')
	cccc
    print("Response:")
    print(speech)

    slack_message = {
        "text": speech,
        "attachments": [
            {
                "title": channel.get('title'),
                "title_link": channel.get('link'),
                "color": "#36a64f",

                "fields": [
                    {
                        "title": "Condition",
                        "value": "Temp " + condition.get('temp') +
                                 " " + units.get('temperature'),
                        "short": "false"
                    },
                    {
                        "title": "Wind",
                        "value": "Speed: " + channel.get('wind').get('speed') +
                                 ", direction: " + channel.get('wind').get('direction'),
                        "short": "true"
                    },
                    {
                        "title": "Atmosphere",
                        "value": "Humidity " + channel.get('atmosphere').get('humidity') +
                                 " pressure " + channel.get('atmosphere').get('pressure'),
                        "short": "true"
                    }
                ],

                "thumb_url": "http://l.yimg.com/a/i/us/we/52/" + condition.get('code') + ".gif"
            }
        ]
    }

    print(json.dumps(slack_message))

    return {
        "speech": speech,
        "displayText": speech,
        #"data": {"slack": slack_message},
        # "contextOut": [],
        "source": "mytestweatherapp"
    }


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print "Starting app on port %d" % port

    app.run(debug=False, port=port, host='0.0.0.0')
