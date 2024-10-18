from ntscraper import Nitter
from pymongo import MongoClient
import time
from textblob import TextBlob


# Define a list of Nitter instances to rotate through - fremder code (Nitter github : https://github.com/zedeus/nitter )
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://xcancel.com",
    "https://nitter.lacontrevoie.fr",
    "https://nitter.42l.fr",
    "https://nitter.snopyta.org",
    "https://nitter.moomoo.me",
    "https://nitter.pussthecat.org",
    "https://nitter.lucabased.xyz",
    "https://nitter.privacydev.net"
]

# Set search term and hashtag (no language filter)
search_query = "eiffel OR la tour eiffel OR #toureiffel OR #latoureiffel"

# Filtering options
FILTER_OPTIONS = {
    'keywords_include': ['eiffel', 'paris', 'tower', 'toureiffel'],  # Tweets must contain one of these words
    'keywords_exclude': ['advertisement', 'promo'],  # Tweets must not contain these words
    'min_likes': 5,  # Minimum number of likes to store tweet
    'min_retweets': 2,  # Minimum number of retweets to store tweet
    'min_comments': 1,  # Minimum number of comments to store tweet
    'hashtags_include': ['#EiffelTower', '#Paris2024', '#CulturalHeritage'],  # Tweets müssen diese Hashtags enthalten
    'hashtags_exclude': ['#Ad', '#Sponsored'],  # Tweets dürfen diese Hashtags nicht enthalten
    'verified_users_only': True,  # Nur Tweets von verifizierten Konten
    'media_includes': ['photo', 'video'],  # Tweets müssen Bilder oder Videos enthalten
    'sentiment': 'positive'  # Tweets müssen eine positive Stimmung haben

}

# Set up MongoDB connection
try:
    client = MongoClient("mongodb+srv://morel:MORTELcode99@cluster1.mw3pd.mongodb.net/")  # MongoDB URI
    db = client['tweet_db']  # Create a database
    collection = db['tweets']  # Create a collection for tweets
    print("Connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)

# Funktion zur Überprüfung der Sentiment-Analyse
def check_sentiment(tweet_text):
    analysis = TextBlob(tweet_text)
    # Sentiment-Werte: polarity (-1 = negativ, 1 = positiv) und subjectivity
    sentiment_polarity = analysis.sentiment.polarity
    sentiment_subjectivity = analysis.sentiment.subjectivity

    if FILTER_OPTIONS['sentiment'] == 'positive' and sentiment_polarity > 0.1:
        return True
    elif FILTER_OPTIONS['sentiment'] == 'negative' and sentiment_polarity < -0.1:
        return True
    elif FILTER_OPTIONS['sentiment'] == 'neutral' and -0.1 <= sentiment_polarity <= 0.1:
        return True
    return False

# Funktion, um zu überprüfen, ob ein Tweet die Filterkriterien erfüllt
def tweet_passes_filter(tweet):
    # Überprüfen, ob der Tweet ausgeschlossene Schlüsselwörter enthält
    if any(exclude in tweet['text'].lower() for exclude in FILTER_OPTIONS['keywords_exclude']):
        print(f"Tweet by {tweet['user']['name']} contains excluded keyword(s).")
        return False

    # Überprüfen, ob der Tweet mindestens ein enthaltenes Schlüsselwort enthält
    if not any(include in tweet['text'].lower() for include in FILTER_OPTIONS['keywords_include']):
        print(f"Tweet by {tweet['user']['name']} does not contain required keyword(s).")
        return False

    # Überprüfen, ob der Tweet einen der eingeschlossenen Hashtags enthält
    if not any(hashtag in tweet['text'].lower() for hashtag in FILTER_OPTIONS['hashtags_include']):
        print(f"Tweet by {tweet['user']['name']} does not contain required hashtag(s).")
        return False
    
    # Überprüfen, ob der Tweet keine der ausgeschlossenen Hashtags enthält
    if any(hashtag in tweet['text'].lower() for hashtag in FILTER_OPTIONS['hashtags_exclude']):
        print(f"Tweet by {tweet['user']['name']} contains excluded hashtag(s).")
        return False

    # Überprüfen, ob der Tweet von einem verifizierten Benutzer stammt (falls erforderlich)
    if FILTER_OPTIONS['verified_users_only'] and not tweet['user']['verified']:
        print(f"Tweet by {tweet['user']['name']} is not from a verified account.")
        return False

    # Überprüfen, ob der Tweet Bilder oder Videos enthält (falls erforderlich)
    if FILTER_OPTIONS['media_includes'] and not any(media_type in tweet.get('media', []) for media_type in FILTER_OPTIONS['media_includes']):
        print(f"Tweet by {tweet['user']['name']} does not contain required media content.")
        return False

    # Überprüfen der Mindestanzahl an Likes, Retweets und Kommentaren
    if tweet['stats']['likes'] < FILTER_OPTIONS['min_likes']:
        print(f"Tweet by {tweet['user']['name']} does not meet the minimum likes threshold.")
        return False
    if tweet['stats']['retweets'] < FILTER_OPTIONS['min_retweets']:
        print(f"Tweet by {tweet['user']['name']} does not meet the minimum retweets threshold.")
        return False
    if tweet['stats']['comments'] < FILTER_OPTIONS['min_comments']:
        print(f"Tweet by {tweet['user']['name']} does not meet the minimum comments threshold.")
        return False

    # Überprüfen der Stimmung des Tweets
    if not check_sentiment(tweet['text']):
        print(f"Tweet by {tweet['user']['name']} does not meet the sentiment criteria.")
        return False

    return True

# Function to get a working Nitter instance - eine Mischung von fremdem und eigenem Code inspiriert bei Lorenzo Bocchi : https://github.com/bocchilorenzo/ntscraper/tree/main
def get_working_instance():
    for instance in NITTER_INSTANCES:
        try:
            scraper = Nitter(instance)
            # Test the instance with a sample request
            test_tweets = scraper.get_tweets('eiffel', mode='term', number=1)
            if test_tweets['tweets']:
                print(f"Using instance: {instance}")
                return scraper
        except Exception as e:
            print(f"Instance {instance} failed with error: {e}")
    print("All instances failed. Retrying in 60 seconds...")
    return None

# Function to store tweets in MongoDB
def store_tweets(tweets_data):
    for tweet in tweets_data['tweets']:
        if tweet_passes_filter(tweet):  # Only store tweets that pass the filter
            tweet_data = {
                'link': tweet['link'],
                'text': tweet['text'],
                'user': tweet['user']['name'],
                'likes': tweet['stats']['likes'],
                'retweets': tweet['stats']['retweets'],
                'comments': tweet['stats']['comments'],
                'timestamp': time.time(),
                'media': tweet.get('media', None),
                'sentiment': TextBlob(tweet['text']).sentiment.polarity  # Stimmung des Tweets speichern

            }
            # Insert the tweet into MongoDB if it's not already there (check by 'link')
            if not collection.find_one({"link": tweet['link']}):
                collection.insert_one(tweet_data)
                print(f"Tweet by {tweet['user']['name']} stored.")
            else:
                print(f"Duplicate tweet by {tweet['user']['name']} ignored.")
        else:
            print(f"Tweet by {tweet['user']['name']} did not pass filters.")


# Real-time scraping loop
while True:
    scraper = get_working_instance()
    if scraper is None:
        time.sleep(60)  # Wait 60 seconds before retrying all instances
        continue

    try:
        print("Scraping tweets using term and hashtag search...")
        # Scrape tweets in real-time using both term and hashtag search
        tweets_data = scraper.get_tweets(search_query, mode='term', number=10)

        if tweets_data['tweets']:
            store_tweets(tweets_data)  # Store tweets in MongoDB
        else:
            print("No new tweets found.")
        
        # Wait for 60 seconds to avoid hitting rate limits
        time.sleep(60)

    except ValueError as e:
        print(f"Instance error: {e}. Switching to next instance.")
        time.sleep(5)  # Pause briefly before switching instances
    except KeyboardInterrupt:
        print("Scraping stopped manually.")
        break
    except Exception as e:
        print(f"Unexpected error: {e}")
        time.sleep(60)  # Wait before retrying
