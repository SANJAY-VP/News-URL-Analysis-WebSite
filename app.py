# importing flask and related functions, classes and other libraries
import os
from flask import Flask, render_template, url_for, redirect, request, session
from authlib.integrations.flask_client import OAuth
from google_auth_oauthlib.flow import Flow
import json
import psycopg2
import validators
import nltk
import re
import textstat
from nltk import sent_tokenize
from nltk import word_tokenize
from nltk.sentiment import SentimentIntensityAnalyzer
from nltk.corpus import wordnet
from bs4 import BeautifulSoup
import textstat

# creating instance of classes
app = Flask(__name__)
oauth = OAuth(app)


# authentication for google and github
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GITHUB_CLIENT_ID'] = "542a5ba9738a74d76482"
app.config['GITHUB_CLIENT_SECRET'] = "9d18f20f44caea0695f8615198bbc4613c5c08aa"
app.config['SECRET_KEY'] = "THIS SHOULD BE SECRET"
app.config['GOOGLE_CLIENT_ID'] ="505426678128-m50t4vd86378ueu1mb0ttiv3jvh0hpd7.apps.googleusercontent.com"
app.config['GOOGLE_CLIENT_SECRET'] = "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"
github = oauth.register (
  name = 'github',
    client_id = app.config["GITHUB_CLIENT_ID"],
    client_secret = app.config["GITHUB_CLIENT_SECRET"],
    access_token_url = 'https://github.com/login/oauth/access_token',
    access_token_params = None,
    authorize_url = 'https://github.com/login/oauth/authorize',
    authorize_params = None,
    api_base_url = 'https://api.github.com/',
    client_kwargs = {'scope': 'user:email'},
)
google = oauth.register(
    name = 'google',
    client_id = app.config["GOOGLE_CLIENT_ID"],
    client_secret = app.config["GOOGLE_CLIENT_SECRET"],
    access_token_url = 'https://accounts.google.com/o/oauth2/token',
    access_token_params = None,
    authorize_url = 'https://accounts.google.com/o/oauth2/auth',
    authorize_params = None,
    api_base_url = 'https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint = 'https://openidconnect.googleapis.com/v1/userinfo',  # This is only needed if using openId to fetch user info
    client_kwargs = {'scope': 'openid email profile'},
)
client_secrets_file = 'app.json'
scopes = ['https://www.googleapis.com/auth/userinfo.profile',
          'https://www.googleapis.com/auth/userinfo.email',
          'openid']
redirect_uri = 'http://127.0.0.1:5000/callback'
flow = Flow.from_client_secrets_file(client_secrets_file, scopes=scopes, redirect_uri=redirect_uri)

# connecting to database to store analysis
conn=psycopg2.connect(host='dpg-cnll32q1hbls738r28k0-a',database='mynewpsql',user='mynewpsql_user',password='gJuvm0l7QaVjUhjz8x6ayjgszrMFOQ13')
cur=conn.cursor()

# 'postgres://mynewpsql_user:gJuvm0l7QaVjUhjz8x6ayjgszrMFOQ13@dpg-cnll32q1hbls738r28k0-a:5432/mynewpsql'

# cur.execute("CREATE TABLE news_count (word_count INT,sentence_count INT,stop_count INT, tag_count JSONB, text varchar(300))")
# conn.commit()

# functions used to analyse the data
def sentence_count(text):  # to count number of sentences 
    sentence_list=sent_tokenize(text)
    return len(sentence_list)
def word_count(text):  # to count number of words
    word_list=word_tokenize(text)
    symbol_list=['~','!','#','@','$','%','^','&','*','(',')','_','.',',','?']
    count=0
    for i in word_list:
        if i not in symbol_list:
            count+=1
    return count
def stop_word_count(text): # # to count number of stopwords
    stop_list=nltk.corpus.stopwords.words('english')
    word_list=word_tokenize(text)
    count=0
    for i in word_list:
        if i in stop_list:
            count+=1
    return count
def tag_count(text):  # to count number of UPOS tags
    word_list=word_tokenize(text)    
    upos_tag_list=nltk.pos_tag(word_list,tagset='universal')
    tag_dict={}
    for i in upos_tag_list:
        if i[1] not in tag_dict:
            tag_dict[i[1]]=0
    for i in tag_dict:
        count=0
        for j in upos_tag_list:
            if j[1]==i:
                count+=1
        tag_dict[i]=count
    json_data = json.dumps(tag_dict)
    return json_data
def wordlength(url): # to count the length of each word
    text=content(url)
    len_dict={}
    word_list=list(text.split())
    for i in word_list:
        if len(i) in len_dict:
            len_dict[len(i)]+=1
        elif len(len_dict)>10:
            len_dict[10]+=1
        else:
            len_dict[len(i)]=1
    total_len=sum(len_dict.values())
    for i,j in len_dict.items():
        len_dict[i]=round(j*100/total_len,2)
    sorted_dict=dict(sorted(len_dict.items(), key=lambda item: item[0]))
    return sorted_dict
def title(url): # extracting the news title from text
    from urllib import request
    html=request.urlopen(url).read().decode('utf8')
    soup=BeautifulSoup(html,'html.parser')
    return str(soup.title)[7:-8]
def content(url): # extracting the whole news from url
    from urllib import request
    html=request.urlopen(url).read().decode('utf8')
    soup=BeautifulSoup(html,'html.parser')
    string=str(soup.find_all(type="application/ld+json")[1])
    start=string.find('articleBody')+14
    end=string.find('Follow The New Indian Express channel on')
    if string[start:start+3].isupper():
        string=string[start:end-1]
        for i, c in enumerate(string):
            if c=='.' and i+1<len(string) and string[i+1]!=' ':
                string=string.replace('.','. ')
        string=re.sub(r'\\','',string)
        string=re.sub(r'\ &nbsp;','',string)
        # string = re.sub(r'\. \..*?[\.\?]','.', string)
        return string
    else:
        string="FETCH THE URL INSIDE THE NEWS PAPER !"
        return string
def plotcreator(text): # analysing sentiments of given text
    sia = SentimentIntensityAnalyzer()
    sentiment_scores = sia.polarity_scores(text)
    y = [sentiment_scores['neg'],sentiment_scores['neu'],sentiment_scores['pos']]
    return  (round(y[0]*100,2),round(y[1]*100,2),round(y[2]*100,2))
def get_text_difficulty(text): # extracting most difficult words from the text
    # word_list = text.split()
    word_list =word_tokenize(text)
    word_difficulty = {}
    for word in word_list:
        try:
            grade_level = textstat.text_standard(word, float_output=True)
            word_difficulty[word] = grade_level
        except Exception as e:
            pass
    sorted_word_difficulty = dict(sorted(word_difficulty.items(), key=lambda item: item[1], reverse=True))
    first_30_words = list(sorted_word_difficulty.keys())[:17]
    return first_30_words
def get_synonyms(word): # to get the synonyms of a given word
    synonyms = []
    for syn in wordnet.synsets(word):
        for lemma in syn.lemmas():
            synonyms.append(lemma.name())
    if len(list(set(synonyms)))!=0:
        return list(set(synonyms)) 
    else:
        return 'No Data Found'
def valid_email_password(email,password): # validating the email and password
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    password_pattern='^.{6,}$'
    if re.match(email_pattern, email):
        if re.match(password_pattern,password):
            return True
        else:
            return False
    else:
        return False

# home page
@app.route("/",methods=["POST","GET"])
def portal0():
    return render_template('home.html')

# main page where analysis is done
@app.route("/input",methods=["POST","GET"])
def portal1():
    count=''  
    link=''
    head=''
    vocabulary=''
    if request.method=="POST" :
        link=request.form.get('paragraph')
        try:
            if not validators.url(link):
                return render_template("newsapp.html",msg_url_warning=0,msg_plot=0)
            count=content(link)
            head=title(link)
            vocabulary=get_text_difficulty(count)
            len_count=wordlength(link)
            if count=="FETCH THE URL INSIDE THE NEWS PAPER !":
                return render_template("newsapp.html",msg_url_warning=1,msg_plot=plotcreator(count))
            if len(link)<500:
                cur.execute('INSERT INTO news_count (word_count ,sentence_count ,stop_count ,tag_count,text)values(%s,%s,%s,%s,%s)',(word_count(count),sentence_count(count),stop_word_count(count),tag_count(count),link))
                conn.commit()     
        except:
            return render_template("newsapp.html",msg_url_warning=1,msg_plot=0)
    return render_template("newsapp.html",msg_word= word_count(count),msg_sentences=sentence_count(count),msg_stop=stop_word_count(count),msg_tag=tag_count(count),
       word_len_counter=len_count,msg_count=len(link),msg=count,msg_plot=plotcreator(count),msg_title=head,msg_vocabulary=vocabulary) 

# admin login to access table
@app.route("/adminlogin",methods=["POST","GET"])
def portal2():   
    table_data=''
    new_mail=''
    new_pass=''
    if request.method=="POST":
        new_mail=request.form.get("Email")
        new_pass=request.form.get("password")  
        cur.execute('select * from news_count')
        table_data=cur.fetchall()
    return render_template("table.html",msg_tab=table_data,msg_new_mail=new_mail,msg_new_pass=new_pass,msg_count=0,msg_plot=0) 
       
# synonym finding 
@app.route("/synpage",methods=["POST","GET"])
def portal3():
    word=''
    if request.method=="POST":
                word=request.form.get('inputword')
    return render_template("newsapp.html",msg_synonym=get_synonyms(word),msg_plot=0)

# login in a normal way
@app.route("/loginnormal",methods=["POST","GET"])
def portal4():
    return render_template("login.html")
    # email=""
    # password=""
    # table=""
    # if request.method=="POST":
    #     email=request.form.get('Email') 
    #     password=request.form.get('Password') 
    #     cur.execute('INSERT INTO user_info (EMAIL,PASSWORD) VALUES (%s,%s)',(email,password))
    #     conn.commit()
    #     return render_template("login.html", msg_email=email,msg_password=password,msg_table=table,msg_regist=1)
    # return render_template("login.html", msg_email=email,msg_password=password,msg_table=table,msg_regist=0)

# login the user 
@app.route('/userlogin',methods=["POST","GET"])
def portal5():
    email=''
    password=''
    if request.method=="POST" :
        email=request.form.get('Gmail')
        password=request.form.get('Password')
        if valid_email_password(email,password):
            return render_template('newsapp.html',msg_email=email,msg_pass=password,msg_plot=0)
        else:
            return render_template('login.html',msg_email=0,msg_pass=0,msg_plot=0)
    return render_template('login.html',msg_email=1,msg_plot=0)

@app.route('/usersignin',methods=["POST","GET"])
def portal6():
    email=''
    password=''
    if request.method=="POST" :
        email=request.form.get('Gmail')
        password=request.form.get('Password')
        if valid_email_password(email,password):
            return render_template('newsapp.html',msg_email=email,msg_pass=password,msg_plot=0)
        else:
            return render_template('signin.html',msg_email=0,msg_pass=0,msg_plot=0)
    return render_template('signin.html',msg_email=1,msg_plot=0)

#  a portal for showing the table
@app.route('/table',methods=["POST","GET"])
def table():
    return render_template('table.html')

# login using github authentication
@app.route('/login',methods=["POST","GET"])
def github_login():
    github = oauth.create_client('github')
    redirect_uri = url_for('github_authorize', _external=True)
    return github.authorize_redirect(redirect_uri)
@app.route('/login/github/authorize')
def github_authorize():
    github = oauth.create_client('github')
    token = github.authorize_access_token()
    resp = github.get('user').json()
    print(f"\n{resp}\n")
    return render_template('newsapp.html',msg_email=token,msg_plot=0)

# login using google authentication  
@app.route('/index')
def index():
    if 'google_token' in session:
        return redirect(url_for('protected'))
    else:
        authorization_url, _ = flow.authorization_url(prompt='consent')
        return redirect(authorization_url)
@app.route('/callback')
def callback():
    flow.fetch_token(code=request.args.get('code'))
    session['google_token'] = flow.credentials.token
    return redirect(url_for('protected'))
@app.route('/protected')
def protected():
    if 'google_token' in session:
        return render_template("newsapp.html",msg_plot=0) 
    else:
        return redirect(url_for('index'))

# if __name__=='__main__':
#     app.run(debug=True)
