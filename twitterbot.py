#
# Twitter Bot Using AI for Smart Home DB
#
import tweepy
import openai
import random	
import keys		   			# my secret keys for Twitter API and OpenAI API
import rssparser as rss  	# my RSS parser and data generator
import pandas as pd

_filename_users = 'latest_twitter_user_news.csv'
_filename_keywords = 'latest_twitter_keyword_news.csv'

def twitter_api():
	auth = tweepy.OAuthHandler(keys.api_key, keys.api_secret)
	auth.set_access_token(keys.access_token, keys.access_token_secret)

	return tweepy.API(auth)

def gen_tweet(str,lnk):
	openai.api_key = keys.openai_key
	tweet = openai.Completion.create(engine="text-davinci-003",prompt="tweet something cool (only one sentence) for this (also add related SEO hashtags but do not add any URL): " + str + " which is found in the link here: " + lnk, max_tokens=64)

	return tweet.choices[0].text

def tweet(api: tweepy.API, message:str, image_path=None):
	api.update_status(message)	
	print('Tweeted successfully!')

def user_tweets(the_user, b_save):
	user = the_user
	limit = 300

	tweets = tweepy.Cursor(_api.user_timeline, screen_name=user, count=200, tweet_mode='extended').items(limit)

	columns = ['Time','User','Tweet']
	data = []

	for tweet in tweets:
		data.append([tweet.created_at, tweet.user.screen_name, tweet.full_text])

	df = pd.DataFrame(data, columns=columns)

	if (b_save):
		df.to_csv(_filename_users, columns=columns, encoding='utf-8')    	

	print(df)


def keyword_tweets(the_keywords, b_save):
	keywords = the_keywords
	limit = 300

	tweets = tweepy.Cursor(_api.search_tweets, q=keywords, count=100, tweet_mode='extended').items(limit)

	columns = ['Time','User','Tweet']
	data = []

	for tweet in tweets:
		data.append([tweet.created_at, tweet.user.screen_name, tweet.full_text])

	df = pd.DataFrame(data, columns=columns)

	if (b_save):
		df.to_csv(_filename_keywords, columns=columns, encoding='utf-8')    	

	print(df)

def auto_tweet():
	data = rss.get_data_records()
	print(data.title)	
	print(data.url)		
	print(data.shorturl)
	the_tweet = ""
	try:
		the_tweet = gen_tweet(data.title, data.url)
	except:
		the_tweet = data.title + " " + data.shorturl
	
	#the_tweet = the_tweet + " " + data.shorturl
	print("The tweet to generate is: " + the_tweet)			
	#api = twitter_api()
	#tweet(_api, the_tweet)

def test():
	user_tweets('@snowden', 'yes')
	keyword_tweets('security', 'yes')
	#rss.get_data_records()

if __name__ == '__main__':
	_api = twitter_api()
	auto_tweet()
	#test()
