from datetime import datetime, timedelta


class TimeStamp:

    def __init__(self):
        self.time_now = datetime.now()
        self.time_old = self.time_now
        self.time_dif = self.time_now - self.time_old
        self.time_old = self.time_now

    def timestamp(self):
        self.time_now = datetime.now()
        self.time_dif = self.time_now - self.time_old
        self.time_old = self.time_now

    def timesstampdiff(self):
        self.time_dif

