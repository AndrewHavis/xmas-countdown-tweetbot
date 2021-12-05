import datetime

from pytz import timezone
from src import app as countdown
from time import sleep

if __name__ == "__main__":
    # Send a tweet every day at 12:00 London time.
    time_format = "%H:%M"
    while True:
        if datetime.datetime.now(tz=timezone("Europe/London")).strftime(time_format) == "12:00":
            countdown.XmasCountdownBotApp().tweet()
            sleep(60)
