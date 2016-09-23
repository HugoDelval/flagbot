
class Duration:
    def __init__(self, days, hours):
        self.days = days
        self.hours = hours

    def __init__(self, json_duration):
        try:
            self.days = json_duration["days"]
        except Exception as e:
            self.days = 0
        try:
            self.hours = json_duration["hours"]
        except Exception as e:
            self.hours = 0


class CtfTimeEvent:
    
    def __init__(self, json_ctftime):
        self.organizers = json_ctftime["organizers"] or []
        self.onsite = json_ctftime["onsite"] or True
        self.finish_ts = json_ctftime["finish"] or "2015-01-18T17:30:00+00:00"
        self.description = json_ctftime["description"] or "the description"
        self.weight = json_ctftime["weight"] or 0
        self.title = json_ctftime["title"] or "The Title"
        self.url = json_ctftime["url"] or "http://google.com"
        self.is_votable_now = json_ctftime["is_votable_now"] or False
        self.restrictions = json_ctftime["restrictions"] or "Unknown"
        self.format = json_ctftime["format"] or "Unknown"
        self.start_ts = json_ctftime["start"] or "2015-01-16T20:30:00+00:00"
        self.participants = json_ctftime["participants"] or 0
        self.ctftime_url = json_ctftime["ctftime_url"] or "https://ctftime.org/"
        self.location = json_ctftime["location"] or "Washington, DC"
        self.live_feed = json_ctftime["live_feed"] or "??"
        self.public_votable = json_ctftime["public_votable"] or False
        self.duration = Duration(json_ctftime["duration"]) or Duration(0,0)
        self.logo = json_ctftime["logo"] or ""
        self.format_id = json_ctftime["format_id"] or -1
        self.id = json_ctftime["id"] or -1
        self.ctf_id = json_ctftime["ctf_id"] or -1
        self.json = json_ctftime
   
    def __str__(self):
        return "JSON representation : " + str(self.json)
