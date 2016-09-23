import json
import requests
import datetime, time
import ctftime_object
from dateutil.parser import parse

url_ctftime = "https://ctftime.org/api/v1"
event_endpoint = "/events/"

# Take in parameter an integer event_id
# return a ctftime_object.CtfTimeEvent object 
#        describing the event event_id.
# return an error string if there is one
def get_event(event_id):
    event_id = int(event_id)
    res_event = requests.get(url_ctftime + event_endpoint + str(event_id) + '/')
    if res_event.status_code != 200:
        return "An error occured during the request to ctftime.org Status code : " + str(res_event.status_code)
    try:
        json_resp = json.loads(res_event.text)
    except Exception as e:
        return "An error occured during parsing json from ctftime.org : " + str(e)
    return ctftime_object.CtfTimeEvent(json_resp)

# Take in parameter an optionnal integer number_of_weeks
# return a list of ctftime_object.CtfTimeEvent object 
#        describing the next events in the following weeks.
# return a error string if there is one
def get_next_events(number_of_weeks=1):
    number_of_weeks = int(number_of_weeks)
    if number_of_weeks < 1 or number_of_weeks > 10:
        return "An error occured during the request to ctftime.org The number of weeks should be >= 1 and <=10"
    current_time = int(time.time())
    next_time = current_time + (60*60*24*7*number_of_weeks) 
    res_next_events = requests.get(url_ctftime + event_endpoint + "?limit=100&start=" + str(current_time) + "&finish=" + str(next_time + (60*60*24*7))) # we take 1 week more and then filter
    if res_next_events.status_code != 200:
        return "An error occured. Status code : " + str(res_next_events.status_code)
    try:
        json_resp = json.loads(res_next_events.text)
        json_resp = [json_ctf for json_ctf in json_resp if int(time.mktime(parse(json_ctf["start"]).timetuple())) < next_time]
    except Exception as e:
        return "An error occured during parsing json from ctftime.org : " + str(e)
    return [ctftime_object.CtfTimeEvent(json_ctf) for json_ctf in json_resp]

if __name__ == '__main__':
    print(get_event(165))
    for e in get_next_events():
        print(e)
