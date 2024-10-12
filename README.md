# Twitter Scraping Project - Real-Time Tweet Collection

This project allows you to scrape tweets related to the Eiffel Tower and other cultural heritage keywords in real-time, filter them based on various criteria, and store the results in a MongoDB database. The system uses Nitter instances to scrape publicly available tweets and includes filters such as sentiment analysis, media presence, and engagement metrics.

## Features
- **Real-Time Tweet Collection**: Fetch tweets in real-time using Nitter.
- **Sentiment Analysis**: Filter tweets based on sentiment (positive, negative, or neutral) using TextBlob.
- **Media and Hashtag Filters**: Collect only tweets with images, videos, and specific hashtags.
- **Engagement Thresholds**: Filter tweets based on the minimum number of likes, retweets, and comments.
- **Verified Users**: Optionally collect only tweets from verified users.
- **MongoDB Storage**: Store all collected and filtered tweets in MongoDB for future analysis.

## Requirements

To run this project, you need to have the following installed:

1. **Python 3.x**
2. **MongoDB** (Either locally or using MongoDB Atlas)
3. **Nitter** (via `ntscraper` package)
4. **Required Python Libraries**:
    - `pymongo`
    - `textblob`
    - `ntscraper`

## Installation

### 1. Clone the Project
First, clone the repository to your local machine:

```bash
git clone https://github.com/your-username/twitter-scraping-project.git
cd twitter-scraping-project
```

### 2. Install Dependencies
You can install the required dependencies using `pip`. Ensure that you are in the project directory:

```bash
pip install pymongo textblob ntscraper
```

Additionally, you will need the `textblob` corpora for sentiment analysis:

```bash
python -m textblob.download_corpora
```

### 3. Set Up MongoDB
Ensure that you have MongoDB running locally or you have a MongoDB Atlas instance set up. You can create a MongoDB Atlas cluster for free at [mongodb.com](https://www.mongodb.com).

1. **Local MongoDB**:
   If you're using MongoDB locally, ensure the service is running on the default port (`localhost:27017`).

2. **MongoDB Atlas**:
   If you're using MongoDB Atlas, replace the MongoDB connection string in the script with your connection URI.

### 4. Configure the Project

The project uses the Nitter scraper to fetch tweets and MongoDB to store the data. In the code, you need to modify the MongoDB connection string and adjust other settings such as the search query and filter options.

#### MongoDB Connection
In the script, ensure the MongoDB connection is correctly configured:

```python
# Set up MongoDB connection
try:
    client = MongoClient("mongodb+srv://<your_username>:<your_password>@<your_cluster>.mongodb.net/")  # MongoDB URI
    db = client['tweet_db']  # Database
    collection = db['tweets']  # Collection
    print("Connected to MongoDB.")
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")
    exit(1)
```

Replace `<your_username>`, `<your_password>`, and `<your_cluster>` with your MongoDB credentials.

### 5. Run the Script

Once everything is configured, you can run the script:

```bash
python twitter_scraper.py
```

The script will begin scraping tweets based on the search query and filter them according to your settings. Filtered tweets will be stored in your MongoDB database.

## How It Works

1. **Nitter Instances**: The script uses a rotating list of Nitter instances to scrape tweets from Twitter without requiring the official Twitter API.
   
2. **Search and Filter**: The script searches for tweets related to the Eiffel Tower using a set of keywords and hashtags, and filters them based on:
   - Sentiment (positive/negative/neutral)
   - Presence of media (photos/videos)
   - Minimum number of likes, retweets, and comments
   - Verified accounts

3. **MongoDB Storage**: All filtered tweets are saved in a MongoDB collection, with metadata such as the tweet's text, user info, engagement data (likes, retweets), and sentiment score.

### Filter Criteria

You can modify the filtering options to suit your needs. Here is the default configuration:

```python
FILTER_OPTIONS = {
    'keywords_include': ['eiffel', 'paris', 'tower', 'toureiffel'],
    'keywords_exclude': ['advertisement', 'promo'],
    'min_likes': 5,
    'min_retweets': 2,
    'min_comments': 1,
    'hashtags_include': ['#EiffelTower', '#Paris2024', '#CulturalHeritage'],
    'hashtags_exclude': ['#Ad', '#Sponsored'],
    'verified_users_only': True,
    'media_includes': ['photo', 'video'],
    'sentiment': 'positive'
}
```

You can adjust these filters by editing the corresponding dictionary keys.

### Example Output

The collected tweets are stored in MongoDB with the following structure:

```json
{
    "link": "https://twitter.com/...",
    "text": "Amazing view of the Eiffel Tower!",
    "user": "username",
    "likes": 120,
    "retweets": 30,
    "comments": 10,
    "timestamp": 1689000000,
    "media": ["photo"],
    "sentiment": 0.85
}
```

## Additional Features

### Sentiment Analysis
The script uses `TextBlob` for sentiment analysis. You can configure whether you want to collect positive, negative, or neutral tweets.

```python
def check_sentiment(tweet_text):
    analysis = TextBlob(tweet_text)
    sentiment_polarity = analysis.sentiment.polarity
    if FILTER_OPTIONS['sentiment'] == 'positive' and sentiment_polarity > 0.1:
        return True
    elif FILTER_OPTIONS['sentiment'] == 'negative' and sentiment_polarity < -0.1:
        return True
    elif FILTER_OPTIONS['sentiment'] == 'neutral' and -0.1 <= sentiment_polarity <= 0.1:
        return True
    return False
```

### Rotating Nitter Instances
If one Nitter instance fails, the script will automatically switch to the next available instance:

```python
NITTER_INSTANCES = [
    "https://nitter.poast.org",
    "https://xcancel.com",
    "https://nitter.lacontrevoie.fr",
    "https://nitter.42l.fr"
]
```

## Future Enhancements
- **Web Interface**: Build a simple Flask or Django web application to display the collected tweets in real-time.
- **Machine Learning Filters**: Integrate machine learning models to automatically adjust filters based on trends or tweet content.

## Legal Considerations

Be aware of the legal implications of scraping content. While scraping publicly available tweets is generally legal, be cautious when dealing with copyrighted material (e.g., images, videos) and always comply with Twitter’s terms of service.

## Conclusion

This project demonstrates how to scrape, filter, and store real-time tweets using Nitter and MongoDB. The system can be adapted to various use cases, such as trend analysis, sentiment monitoring, or cultural heritage studies.

Feel free to contribute to this project by creating a pull request or reporting issues!

---

If you have any questions or encounter issues, feel free to contact me at `tchoubou@th-brandenburg.de`.
