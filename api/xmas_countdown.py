import datetime as dt


class XmasCountdown:

    def __init__(self):
        # If it is on or before Christmas Day this year (25th December), calculate the time until Christmas Day this year.
        # Otherwise, calculate the time until Christmas Day next year.
        # Therefore, if it is the 24th December, it should be one day until Christmas Day.
        # If it is the 25th December, it should be zero days.
        # If it is the 26th December, it should be 364 days (or 365 if next year is a leap year).
        self.today = dt.date.today()
        self.xmas_dates = {
            "this_year": dt.date(self.today.year, 12, 25),
            "next_year": dt.date(self.today.year + 1, 12, 25)
        }
        self.xmas_date = self.xmas_dates["this_year"] if self.today <= self.xmas_dates["this_year"] else self.xmas_dates["next_year"]

    def get_time_until_xmas(self):
        return self.xmas_date - self.today

    def get_days_until_xmas(self):
        return self.get_time_until_xmas().days


if __name__ == "__main__":
    countdown = XmasCountdown()
    print(countdown.get_days_until_xmas())
