# News URL Analysis Website

**Website Link:** [News URL Analysis](https://renderdemo-hwtw.onrender.com)

**Contributor:** Sanjay V P

---

## Introduction
This report details the features and analysis of *urlbee*, a web application designed to analyze news URLs. *Urlbee* allows users to count words, sentences, stop words, and UPOS tags. It also provides features to identify difficult words and measure readability. The application is built using Flask, integrates with a PostgreSQL database, and is deployed on Render.com.

---

## Features

### Content Analysis
- Analyze the given URL to calculate:
  - Number of words.
  - Number of sentences.
  - Number of stop words.
  - UPOS (Universal Part-of-Speech) tag counts.

### Vocabulary Analysis
- Identify the most difficult words in the text.
- Provide synonyms for these words using WordNet.

### Readability Analysis
- Calculate the length of all words in the text.
- Determine the percentage composition of words by length.

### Analysis Storage
- Stores the entire analysis in a dedicated table, accessible only to the admin.

### Authentication
- Supports Google and GitHub authentication using OAuth and oauthlib.

---

## Algorithms Used

1. **Sentence and Word Count**: Utilizes NLTK's built-in functionalities.
2. **Stop Words Count**: Compares each word against a predefined list of stop words.
3. **UPOS Tagging**: Determines the type of each word and stores it in a UPOS dictionary.
4. **Web Scraping**: Uses BeautifulSoup and Regex to extract titles and content.
5. **Sentiment Analysis**: Implements TextBlob for sentiment analysis.
6. **Grade Level Analysis**: Employs the TextStat library to identify high-grade (difficult) words.
7. **Synonyms**: Uses WordNet to provide synonyms for difficult words.
8. **Input Validation**: Leverages regular expressions to validate email and password formats.
9. **Database Integration**: Connects Flask with PostgreSQL using Psycopg2.

---


## Conclusion
The News URL Analysis website empowers users to understand the content, tone, and complexity of news articles. It is a valuable tool for researchers, students, and anyone seeking to delve deeper into news media analysis.

---

## How to Use
1. Clone the repository.
2. Install required Python packages using `pip install -r requirements.txt`.
3. Start the Flask server using `python app.py`.
4. Open the application in your browser and input a news URL to begin analysis.

---

Explore the application and unlock the potential of news article analysis with a click!

