import datetime
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz

class EST5EDT(datetime.tzinfo):

    def utcoffset(self, dt):
        return datetime.timedelta(hours=-5) + self.dst(dt)

    def dst(self, dt):
        d = datetime.datetime(dt.year, 3, 8)        #2nd Sunday in March
        self.dston = d + datetime.timedelta(days=6-d.weekday())
        d = datetime.datetime(dt.year, 11, 1)       #1st Sunday in Nov
        self.dstoff = d + datetime.timedelta(days=6-d.weekday())
        if self.dston <= dt.replace(tzinfo=None) < self.dstoff:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(0)

    def tzname(self, dt):
        return 'EST5EDT'

class Trail(object):
    def __init__(self, name, status, date):
        self._name = name.strip()
        self._status = status.lower().strip()
        self._date = self._format_date(date)

    def __str__(self):
        return "{}, {}, {}, {}".format(self.name(), self.status(), self.date(), self.age())

    @staticmethod
    def _format_date(date):
        month_day, hour_min, am_pm = date.strip().split()
        month, day = month_day.split('/')
        hour, min = hour_min.split(':')
        now = datetime.datetime.now(tz=EST5EDT())
        if am_pm == 'pm':
            hour = int(hour) + 12
        else:
            hour = int(hour)
        date = datetime.datetime(now.year, int(month), int(day), hour, int(min), 0, tzinfo=EST5EDT())
        # Check if the calculated date is in the future.  If so, subtract a year.  This handles the calendar
        # rollover, since we're not given a year from the website.
        if date > now:
            return date.replace(year = date.year - 1)
        return date

    def name(self):
        return self._name

    def status(self):
        return self._status

    def date(self):
        return self._date

    def is_closed(self):
        if self.status() == "closed":
            return True
        return False

    def is_open(self):
        return not self.is_closed()

    def age(self):
        now = datetime.datetime.now(tz=EST5EDT())
        minutes = int(round((now - self.date()).total_seconds() / 60))
        if minutes < 60:
            if minutes == 1:
                return "1 minute"
            else:
                return "{} minutes".format(minutes)
        elif minutes < 60*24:
            hours = int(round(minutes/60))
            if hours == 1:
                return "about 1 hour"
            else:
                return "about {} hours".format(hours)
        else:
            days = int(round(minutes/60/24))
            if days == 1:
                return "about 1 day"
            else:
                return "about {} days".format(days)    
 
class Trails(object):
    def __init__(self):
        self._trails = []
        html_data = self._get_html()
        self._parse_html(html_data)

    def _get_html(self):
        url = "https://www.trianglemtb.com/"
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'
        req = Request(url, headers={'User-Agent': user_agent})
        return urlopen(req).read()
        
    def _parse_html(self, html):
        soup = BeautifulSoup(html, features="html.parser")
        found_table = False
        for table in soup.find_all('table'):
            row_cnt = 0
            for row in table.find_all('tr'):
                col_cnt = 0
                for col in row.find_all('td'):
                    if col.get_text().strip() == "Current Trail Status":
                        found_table = True
                    if not found_table:
                        break
                    if row_cnt > 0:
                        if col_cnt == 0:
                            name = col.get_text().strip()
                            name = self._translate_name(name)
                        elif col_cnt == 1:
                            status = col.get_text().strip()
                        elif col_cnt == 3:
                            date = col.get_text().strip()
                            trail = Trail(name, status, date)
                            self._append_trail(trail)
                    col_cnt += 1
                if not found_table:
                    break
                row_cnt += 1
            if found_table:
                break

    def _append_trail(self, trail):
        self._trails.append(trail)

    def _translate_name(self, name):
        xlate_table = {
            'Skills Area' : 'Briar Chapel Skills Area',
            'Herndon Loop' : 'Briar Chapel Herndon Loop'
        }
        # Remove non-printable characters
        name = name.encode('ascii', errors='ignore').decode().strip()
        return xlate_table.get(name, name)

    def summary(self, status=None):
        open_trails = []
        closed_trails = []
        statement = ""
        for trail in self._trails:
            print(trail)
            if trail.is_open():
                open_trails.append(trail)
            elif trail.is_closed():
                closed_trails.append(trail)
            if not status:
                statement += "{} is {}.\n".format(trail.name(), trail.status())
        if status == "open":
            trails = open_trails
        elif status == "closed":
            trails = closed_trails
        else:
            return statement
        
        num_trails = len(trails)
        if num_trails == 0:
            return "No trails are {}.".format(status)
        if num_trails == len(self._trails):
            return "All trails are {}.".format(status)
        if num_trails == 1:
            return "{} is {}.".format(trails[0].name(), status)
        if num_trails == 2:
            return "{} and {} are {}.".format(trails[0].name(), trails[1].name(), status)
        for trail in trails:
            if trail == trails[-1]:
                statement += "and {} are {}.".format(trail.name(), status)
            else:
                statement += "{}, ".format(trail.name())
        return statement

    def get_trail(self, fuzzy_trail):
        # Return the best trail name match using fuzzy logic
        trails = []
        score = 0
        for trail in self._trails:
            new_score = fuzz.token_set_ratio(trail.name(), fuzzy_trail)
            if new_score > 80:
                trails.append(trail)
            if new_score > score:
                score = new_score
                winning_trail = trail
        if trails:
            return trails
        return [winning_trail]
