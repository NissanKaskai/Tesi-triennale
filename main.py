import tweepy
from textblob import TextBlob
import pandas as pd
import numpy as np
import re
import matplotlib.pyplot as plt
import datetime
plt.style.use('fivethirtyeight')
import json

with open("data.json", "r") as d:
  jsonData = json.load(d)
    
#allego link per tweepy documentation 
# https://docs.tweepy.org/en/stable/api.html


#twitter API credentials
with open("credentials.json", "r") as d:
    credentials = json.load(d)
# dumps the json object into an element
json_str = json.dumps(credentials)
# load the json to a string
resp = json.loads(json_str)
# extract an element in the response


accessToken = resp["accessToken"]
accessTokenSecret= resp["accessTokenSecret"]
consumerKey = resp["consumerKey"]
consumerSecret = resp["consumerSecret"]

#create the autentication object
auth=tweepy.OAuthHandler(consumerKey, consumerSecret)

# set the access token and access token secret
auth.set_access_token(accessToken, accessTokenSecret)

#create the API object while passing in the auth information
api=tweepy.API(auth, wait_on_rate_limit = True)

number_of_tweets=10000
tweets=[]
likes=[]
time=[]
user=[]



giorno = '15/11/2022'
giornoDatetime = datetime.datetime.strptime(giorno, '%d/%m/%Y')

def tweetPerData():
  for i in tweepy.Cursor(api.search_tweets, q="bitcoin",lang='en', tweet_mode="extended").items(number_of_tweets):
    tweets.append(i.full_text)
    likes.append(i.favorite_count)
    time.append(i.created_at)
    if (len(tweets)%10 ==0):
      print("siamo arrivati al tweet: ", len(tweets))
tweetPerData()



#create a function to clean the tweets
def cleanTwt(twt):
  twt=re.sub('RT','',twt) #remove 'RT' from the tweets
  twt=re.sub('#[A-Za-z0-9]+','',twt) #remove the '#' from the tweets
  twt=re.sub('\\n','',twt) #remove '\n' from the tweets
  twt=re.sub('https?:\/\/\S+','',twt) #remove hyperlinks from the tweets
  twt=re.sub('@[\S]*','',twt) #remove @mentions from the tweets
  twt=re.sub('^[\s]+|[\s]+$','',twt) #remove leading and trailing whitespaces from the tweets
  return twt

#list with cleaned text
cleanedTweets = []
for i in range (len(tweets)):
  newTweet = cleanTwt(tweets[i])
  cleanedTweets.append(newTweet)

#creo una lista con le date in formato datetime per il dataframe
date= []
for i in range (len(time)):
    data = time[i].strftime("%d/%m/%Y")
    date.append(data)


#create a new dataframe
df=pd.DataFrame({'Cleaned_Tweets': cleanedTweets, 'likes':likes, 'time':date, 'ora':time})
#remove any duplicate rows
df.drop_duplicates(subset=['Cleaned_Tweets'], inplace=True)
idx=list(range(0,len(df)))
df=df.set_index(pd.Index(idx))
#create a function to get the polarity
def getPolarity(twt):
  return TextBlob(twt).sentiment.polarity
#create one new column for and polarity
df['Polarity']=df['Cleaned_Tweets'].apply(getPolarity)

#funzione che trova la media di un determinato giorno
def trovaMediaGiornoConLike(giorno):
  nElementi = 0
  media= 0
  for i in range (len(df['Cleaned_Tweets'])):    
    if (datetime.datetime.strptime(df['time'][i],"%d/%m/%Y").day == giorno.day and getPolarity(df['Cleaned_Tweets'][i])) !=0:      
      nElementi = nElementi+df['likes'][i]+1
      media+= getPolarity(df['Cleaned_Tweets'][i])*(df['likes'][i]+1)      
  media = media / nElementi
  return media

giornoInizialeString = giornoDatetime.replace(day=giornoDatetime.day-1)
giornoInizialeString = giornoInizialeString.strftime("%d/%m/%Y")

#aggiorno il file json con il nuovo valore
jsonData[giornoInizialeString] = trovaMediaGiornoConLike(giornoDatetime.replace(day=giornoDatetime.day-1))
with open("data.json", "w") as d:
	json.dump(jsonData, d)


#da utilizzare solo per controllo
numeroTweetConsiderati =0
for i in range (len(df['Cleaned_Tweets'])):  
  if getPolarity(df['Cleaned_Tweets'][i])!=0:
    numeroTweetConsiderati+=1
print(numeroTweetConsiderati)

#print della tabella
df




