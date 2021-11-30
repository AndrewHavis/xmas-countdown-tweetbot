import tweepy
import logging

from os import environ

credentials = {
    "ACCESS_TOKEN": environ.get("TWITTER_ACCESS_TOKEN"),
    "ACCESS_SECRET": environ.get("TWITTER_ACCESS_TOKEN_SECRET"),
    "CLIENT_TOKEN": environ.get("TWITTER_CONSUMER_KEY"),
    "CLIENT_SECRET": environ.get("TWITTER_CONSUMER_SECRET")
}

MAX_TWEET_LENGTH = 280

logging.getLogger().setLevel(logging.INFO)


class Twitter:

    def __init__(self):
        # Starting off in an unauthenticated state where we can access public profiles.
        self.auth = tweepy.OAuthHandler(credentials["CLIENT_TOKEN"], credentials["CLIENT_SECRET"], callback="oob")

        # Add the access tokens if we have them specified already.
        if credentials["ACCESS_TOKEN"] and credentials["ACCESS_SECRET"]:
            self.auth.set_access_token(credentials["ACCESS_TOKEN"], credentials["ACCESS_SECRET"])

        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())
        self.session = {}

    def get_auth_url(self):
        try:
            redirect_url = self.auth.get_authorization_url()
            self.session["request_token"] = self.auth.request_token["oauth_token"]
            return redirect_url
        except tweepy.TweepyException as e:
            logging.error(e)
            logging.error("Error! Failed to get request token.")

    def verification(self, verifier):
        # Get our request token and use it to verify our login.
        token = self.session["request_token"]
        del self.session["request_token"]

        self.auth.request_token = {
            "oauth_token": token,
            "oauth_token_secret": verifier
        }

        try:
            tokens = self.auth.get_access_token(verifier)
            print(self.auth.request_token)
            print("ACCESS TOKEN:", tokens[0])
            print("ACCESS TOKEN SECRET:", tokens[1])
        except tweepy.TweepyException:
            raise tweepy.TweepyException("Error! Failed to get access token.")

        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

    def test_authentication(self):
        try:
            self.api.verify_credentials()
            return True
        except tweepy.TweepyException as e:
            logging.error("Error during authentication!")
            logging.error(e)
            return False

    def logout(self):
        self.auth.access_token = None
        self.auth.access_token_secret = None
        self.api = tweepy.API(self.auth, parser=tweepy.parsers.JSONParser())

    def get_my_info(self):
        try:
            return self.api.verify_credentials()
        except tweepy.TweepyException:
            # We're not logged in as a user, so simply return an ID of None.
            return {
                "id": None
            }

    def tweet(self, tweet_text: str, location: [float, float] = None):
        try:
            if len(tweet_text) <= MAX_TWEET_LENGTH:
                if location:
                    return self.api.update_status(tweet_text, lat=location[0], long=location[1])
                else:
                    return self.api.update_status(tweet_text)
            else:
                # If the tweet is greater than the maximum length (280 characters at time of writing), create a thread.
                # We can do this by splitting the tweet into a list of individual words.
                # We then create a new list that combines the words until we get to the maximum number of characters.
                # Note that I am reducing MAX_TWEET_LENGTH here by 15 to allow for an ellipsis and the tweet number (e.g. 1/5).
                # When the maximum number of characters is reached, a new list item is created.
                split_tweet = tweet_text.split(" ")
                thread_list = []
                thread_part = ""
                for index, word in enumerate(split_tweet):
                    if index < len(split_tweet) - 1:
                        if len(thread_part + word + " ") <= (MAX_TWEET_LENGTH - 15) and index < len(split_tweet):
                            thread_part += word + " "
                        else:
                            thread_list.append(thread_part.strip())
                            thread_part = word + " "
                    else:
                        thread_part += word
                        thread_list.append(thread_part)

                # Add ellipses and tweet numbers as appropriate.
                for index, item in enumerate(thread_list):
                    if index < len(thread_list) - 1:
                        thread_list[index] += f"… ({index + 1}/{len(thread_list)})"
                    else:
                        thread_list[index] += f" ({index + 1}/{len(thread_list)})"

                # Threads require that we tweet the first part of the thread first, and then daisy-chain the rest as replies.
                threaded_tweets = []
                for index, thread_item in enumerate(thread_list):
                    if location:
                        if index == 0:
                            threaded_tweets.append(self.api.update_status(thread_item,
                                                                          lat=location[0] or None,
                                                                          long=location[1] or None
                                                                          ))
                        else:
                            threaded_tweets.append(self.api.update_status(thread_item,
                                                                          in_reply_to_status_id=threaded_tweets[index - 1]["id_str"],
                                                                          lat=location[0] or None,
                                                                          long=location[1] or None
                                                                          ))
                    else:
                        if index == 0:
                            threaded_tweets.append(self.api.update_status(thread_item))
                        else:
                            threaded_tweets.append(self.api.update_status(thread_item,
                                                                          in_reply_to_status_id=threaded_tweets[index - 1]["id_str"]
                                                                          ))

                return threaded_tweets

        except tweepy.TweepyException as error:
            logging.warning("Error returned by Tweepy:")
            logging.warning(error)


if __name__ == "__main__":
    # Run this for testing purposes.
    twitter = Twitter()
    if not twitter.test_authentication():
        url = twitter.get_auth_url()
        print(f"Authorisation URL: {url}")
        verification_code = input("Please enter the verification code: ")
        twitter.verification(verification_code)
    try:
        # This can be run to display access and client tokens and user info for debugging.
        logging.info(twitter.get_my_info())
        print(twitter.auth.access_token, twitter.auth.access_token_secret)
        print(twitter.auth.consumer_key, twitter.auth.consumer_secret)
    except tweepy.TweepyException as err:
        logging.error(err)
