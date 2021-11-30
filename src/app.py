import json

from api import twitter as tw, xmas_countdown as xc


class XmasCountdownBotApp:

    def __init__(self):
        json_file = open("tweet.template.json")
        self.twitter = tw.Twitter()
        self.days_until_xmas = xc.XmasCountdown().get_days_until_xmas()
        self.templates = json.load(json_file)["templates"]
        self.tweet_text = None
        json_file.close()

        self.__authenticate_with_twitter()
        self.__select_tweet_text()

    def __authenticate_with_twitter(self):
        # Only authenticate if we haven't done so already.
        # Otherwise, do nothing here.
        if not self.twitter.test_authentication():
            url = self.twitter.get_auth_url()
            print(f"Authorisation URL: {url}")
            verification_code = input("Please enter the verification code: ")
            self.twitter.verification(verification_code)
        else:
            pass

    def __select_tweet_text(self):
        # Select the tweet text depending on how many days there are left until Christmas.
        if self.days_until_xmas == 0:
            self.tweet_text = self.templates["xmas_day"]
        elif self.days_until_xmas == 1:
            self.tweet_text = self.templates["xmas_eve"]
        else:
            self.tweet_text = self.templates["normal"].replace("nnn", str(self.days_until_xmas))

    def tweet(self):
        return self.twitter.tweet(self.tweet_text)

    def get_tweet_text(self):
        return self.tweet_text
