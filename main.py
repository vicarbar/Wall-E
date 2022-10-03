import os
#from dotenv import load_dotenv
#from matplotlib.cbook import print_cycles # In order to get the api key from the .env file
#load_dotenv()
import telebot
#from telebot import types
from emojiflags.lookup import lookup
from datetime import datetime
from bs4 import BeautifulSoup as bs
import requests
import pandas as pd
import qrcode
import re
from pytube import YouTube
import numpy as np
from textblob import TextBlob
import tweepy
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
from PIL import Image
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from langdetect import detect
from nltk.stem import SnowballStemmer
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from sklearn.feature_extraction.text import CountVectorizer




# Bot implementation
API_TOKEN = os.getenv("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

# Twitter API tokens
API_KEY = os.getenv("API_KEY")
API_KEY_SECRET = os.getenv("API_KEY_SECRET")
ACCESS_TOKEN = os.getenv("ACCESS_TOKEN")
ACCESS_TOKEN_SECRET = os.getenv("ACCESS_TOKEN_SECRET")
BEARER_TOKEN = os.getenv("BEARER_TOKEN")


# Exceptions
class StockNotExistsError(Exception):
    pass

class NetworkError(Exception):
    pass



    
# Scrap Yahoo Finance Api Key in order to get the price and the porcentage of an active
class Price:
    def __init__(self, symbol):

        try:
            url = f"https://finance.yahoo.com/quote/{symbol}"
            network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
        except:
            NetworkError()
            
        if network.status_code == 302:
            raise(StockNotExistsError(symbol))
        
        self.soup = bs(network.text, "html.parser")
        self.symbol = symbol

    
    # Get the current price of an active
    def get_current_price(self):    
        try:
            price = self.soup.find('fin-streamer', {'class': 'Fw(b) Fz(36px) Mb(-4px) D(ib)'}).text
        except AttributeError as error:
            raise StockNotExistsError(self.symbol) from error
        price = price.replace(',','')
        return price
    
    # Get the porcentage of an active
    def get_current_porcentage(self):
        try:
            porc = self.soup.find('fin-streamer', {'data-field':'regularMarketChangePercent'}).text
        except AttributeError as error:
            raise StockNotExistsError(self.symbol) from error
        porc = porc.replace('(','')
        porc = porc.replace(')','')
        porc = porc.replace('%','')
       
        return porc
        
    
    # Get the name of an active given it's symbol
    def get_active_name(self, symbol):
        file = pd.read_csv("activos.csv")
        return file.loc[file.simbolo == symbol].iloc[0,0]
    
    # Format the printing of the price and the porcentage of a single price value
    def format_output(self, symbol, price, porcentage):
        fecha = datetime.today().strftime('%Y-%m-%d')
        hora = datetime.now().strftime("%H:%M:%S")
        act = self.get_active_name(symbol)
        if float(porcentage) > 0:
            emoji = u'\u2B06' + "\U0001F4C8"
        else:
            emoji = u'\u2B07' + "\U0001F4C9"
        if symbol in ["^IBEX", "STOXX50E"]:
            currency = "€"
        else:
            currency = "$"
        output = f"*{fecha} {hora}*\nPrecio del {act}: {price}{currency} {emoji} {porcentage}%"
        return output
    
    # Format the printing of the EUR-USD value
    def eurusd_output(self, price):
        fecha = datetime.today().strftime('%Y-%m-%d')
        hora = datetime.now().strftime("%H:%M:%S")
        if float(price) < 0.95:
            emoji = '\U0001F480'
        elif float(price) < 1:
            emoji = '\U0001F635'
        elif float(price) < 1.05:
            emoji = '\U0001F974'
        elif float(price) < 1.1:
            emoji = '\U0001F915'
        elif float(price) < 1.2:
            emoji = '\U0001F642'
        elif float(price) < 1.3:
            emoji = '\U0001F917'
        else:
            emoji = '\U0001F60E'
        return f"*{fecha} {hora}*\nUn euro equivale a *{price}* dólares {emoji}"
    
    
    


# Get the spanish inflation value
def get_spanish_inflation():
    try:
        url = "https://es.investing.com/economic-calendar/spanish-cpi-961"
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        NetworkError()
        
    soup = bs(network.text, "html.parser")
    date_ini = soup.find('div', {'class': 'releaseInfo'}).text
    date = date_ini.split("anuncio")[1].split("Actual")[0]
    value = date_ini.split("Actual")[1].split("%")[0]
    value = value.replace(',', '.')
    if float(value) < 5:
        emoji = '\U0001F974'
    elif float(value) < 10:
        emoji = '\U0001F635'
    else:
        emoji = '\U0001F631 \U0001F62D'
    return "El valor de la inflación en España" + lookup('ES') + f" actualizado el día *{date}* es de un *{value}%* {emoji}"


# Get the euribor value
def get_euribor():
    try:
        url = "https://www.expansion.com/mercados/euribor.html"
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        pass
    
    # Scraping
    soup = bs(network.text, "html.parser")
    tab = list(soup.find("div", {"class":"col-4 izquierda"}))
    value = str(tab[1]).split("<td>")[1].split("</td>")[0].replace(",",".")
    fecha = datetime.today().strftime('%Y-%m-%d')
    return f"El valor del euribor a {fecha} es *{value}*."


# Get the top5 most active markets according to yahoo finance web
def get_most_active_markets():
    try:
        url = "https://es.finance.yahoo.com/"
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        NetworkError()
    
    # Scraping
    soup = bs(network.text, "html.parser")
    todo = list(soup.find("body").find("ul", {"class":"Carousel-Slider Pos(r) Whs(nw)"}))
    activos = []
    valores = []
    porcentajes = []
    for i in todo:
        b = str(i)
        c = b.split("aria-label=")
        activos.append(list(c[1].split(" class="))[0])
        valores.append(str(c).split("value=")[1].split(">")[0])
        try:
            porcentajes.append(float(str(b).split("C($positiveColor)\">(")[1].split("%)")[0].replace(",", ".")))
        except:
            pass
        try:
            porcentajes.append(float(str(b).split("C($negativeColor)\">(")[1].split("%)")[0].replace(",", ".")))
        except:
            pass
        
    # Delete '"' character from strings
    for i in range(len(activos)):
        activos[i] = activos[i].replace('\"', '')
        valores[i] = valores[i].replace('\"', '')

    # Get the corresponding arrow emoji (up arrow if porcentage goes up and down arrow in other case)
    emojis = []
    up = u'\u2B06'  + "\U0001F4C8" + " +"
    down = u'\u2B07' + "\U0001F4C9"
    for i in porcentajes:
        if i > 0:
            emojis.append(up)
        else:
            emojis.append(down)
    
    
    # Get the current date and time of the info 
    fecha = datetime.today().strftime('%Y-%m-%d')
    hora = datetime.now().strftime("%H:%M:%S")
    
    top_emojis = [u"\u0031" u"\uFE0F" u"\u20E3", u"\u0032" u"\uFE0F" u"\u20E3", u"\u0033" u"\uFE0F" u"\u20E3", u"\u0034" u"\uFE0F" u"\u20E3", u"\u0035" u"\uFE0F" u"\u20E3"]
    
    # Format the output
    output = f"*Mercados más activos a {fecha} {hora}:*\n\n"
    for i in range(len(activos)):
        output = output + f"- {top_emojis[i]} {activos[i]}: {valores[i]} {emojis[i]}{porcentajes[i]}%\n"
        
    return output


# Get the top gainers companies
def get_top_gainers():
    try:
        url = "https://es.finance.yahoo.com/gainers/"
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        NetworkError()
    
    # Scraping
    soup = bs(network.text, "html.parser")
    todo = list(soup.find("tbody"))
    activos = []
    porcentajes = []
    for i in todo:
        a = str(i)
        b = a.split("title=")
        c = str(b[1]).split(">")
        activos.append(c[0])

        porcentajes.append(float(str(str(b[1]).split("%")[3]).split("+")[-1].replace(",", ".")))

        
    # Delete '"' character from strings
    for i in range(len(activos)):
        activos[i] = activos[i].replace('\"', '')    
    
    # Get the current date and time of the info 
    fecha = datetime.today().strftime('%Y-%m-%d')
    hora = datetime.now().strftime("%H:%M:%S")
    
    top_emojis = ["\U0001F947", "\U0001F948", "\U0001F949"]
    
    # Format the output
    output = f"*Principales subidas" + "\U0001F4C8" + f"a {fecha} {hora}:*\n\n"
    for i in range(3):
        output = output + f"{top_emojis[i]} {activos[i]}: +{porcentajes[i]}%\n"
    for i in range(3, len(activos)):
        output = output + f"- {activos[i]}: +{porcentajes[i]}%\n"
        
    return output




# Get the top losers companies
def get_top_losers():
    try:
        url = "https://es.finance.yahoo.com/losers/"
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        NetworkError()
    
    # Scraping
    soup = bs(network.text, "html.parser")
    todo = list(soup.find("tbody"))
    activos = []
    porcentajes = []
    for i in todo:
        a = str(i)
        b = a.split("title=")
        c = str(b[1]).split(">")
        activos.append(c[0])

        porcentajes.append(-float(str(str(b[1]).split("%")[3]).split("-")[-1].replace(",", ".")))

        
    # Delete '"' character from strings
    for i in range(len(activos)):
        activos[i] = activos[i].replace('\"', '')    
    
    # Get the current date and time of the info 
    fecha = datetime.today().strftime('%Y-%m-%d')
    hora = datetime.now().strftime("%H:%M:%S")
    
    top_emojis = ["\U0001F947", "\U0001F948", "\U0001F949"]
    
    # Format the output
    output = f"*Principales bajadas" + "\U0001F4C9" + f"a {fecha} {hora}:*\n\n"
    for i in range(3):
        output = output + f"{top_emojis[i]} {activos[i]}: {porcentajes[i]}%\n"
    for i in range(3, len(activos)):
        output = output + f"- {activos[i]}: {porcentajes[i]}%\n"
        
    return output




# Generate qr code for an specific url 
def get_qr(message):
    url = message.split("qr")[1].strip()
    qr_img = qrcode.make(url)    
    qr_img.save("qr.png")
    



# Download yt video from url
def get_yt(message):
    url = re.split("([yY][tT]|[yY]outube)[\s]", message)[2].strip()
    yt = YouTube(url)
    # Most posible video resolution
    video = yt.streams.get_highest_resolution()
    video.download()
    # ---------------------
    # Rename the video :
    # Look for the modified times of the files in the Wall-E directory
    tiempos = []
    for i in os.listdir():
        tiempos.append(os.path.getmtime(i))
    # Find the last modified file (which is the newly created mp4 video file) and modify it's name
    os.rename(os.listdir()[np.argmax(tiempos)], "video.mp4")
    
    
    
# Format the cinema billoard output
def format_cinema(movies, times, trailers, cinename):
    # Format the output
    fecha = datetime.today().strftime('%Y-%m-%d')
    emojis = ['\U0001F3A5', '\U0001F39F']
    output = f"*Cartelera {cinename} Palencia* {emojis[0]}{emojis[1]} *a día {fecha}:*\n"
    for i in range(len(movies)):
        output = output  + "\n" + "*" + movies[i] + f"* {trailers[i]}\n"
        for j in times[i]:
            output = output + " - " + j + "\n"
    return output
    
    
    
# Get the Ortega or Avenida cinema (Palencia, Spain) billboard
def get_cine(url):
    try:
        network = requests.get(url, headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36"})
    except:
        NetworkError()
        
    # Scraping
    soup = bs(network.text, "html.parser")
    films = list(soup.find("div", {"class":"wcnt"}))
    
    movies = []
    times = []
    trail_urls = []
    
    # Movie titles
    for i in range(2, len(str(films).split("lfilmb")), 2):
        movies.append(str(films).split("lfilmb")[i].split("<span>")[1].split("</span>")[0])

    # Movie schedule
    schedule = list(soup.find_all("div", {"class":"cartelerascont"}))
    sched = str(schedule).split('Digital\">')
    for i in range(len(movies)):
        time = []
        for j in range(1, len(sched)):
            if sched[j - 1].split('content=\"')[1].split('\">')[0].replace('\"/>', '').replace('\n<p class="stn" title="', '') == movies[i]:
                time.append(sched[j].split('content=\"')[0].split("</p>")[0])
        times.append(time)
        
    # Movie trailers link
    trails = list(soup.find_all("div", {"class":"related"}))
    for i in range(1, len(trails) + 1):
        trail_urls.append(str(trails).split('href=\"')[i].split('\">Trailer')[0])
        
    if url == "https://www.ecartelera.com/cines/420,0,1.html":
        cinename = "Teatro Cine Ortega"
    else:
        cinename = "Multicines Avenida"
            
    return format_cinema(movies, times, trail_urls, cinename)





###################################
# TWITTER SENTIMENT ANALYSIS
###################################

# Get Twitter api v2 client
def getClient():
    client = tweepy.Client(bearer_token = BEARER_TOKEN,
                           consumer_key = API_KEY,
                           consumer_secret = API_KEY_SECRET,
                           access_token = ACCESS_TOKEN,
                           access_token_secret = ACCESS_TOKEN_SECRET)
    return client


# Percentage format for numbers
def percentage(part, whole):
    return 100 * float(part)/float(whole)


# Count values in single columns
def count_values_in_column(data, feature):
    total = data.loc[:,feature].value_counts(dropna = False)
    percentage = round(data.loc[:,feature].value_counts(dropna = False, normalize = True)*100,2)
    return pd.concat([total, percentage], axis = 1, keys = ['Total', 'Percentage'])
    


# Format the sentiment analysis output
def sentiment_format(df):
    perc = df['Percentage']
    words = ["neutral", "positive", "negative"]
    emojis = [u'\u2B55', u'\u2705', u'\u274C']
    output = "*Sentiment Analysis:*\n"
    for i in range(3):
        output = output + f"- {words[i]}: {perc[i]}% {emojis[i]}\n"
    return output
    
    
    


# Perform the sentiment analysis based on Twitter messages related to the topic to be analysed
def get_twitter_sentiment_analysis(message):
    # Twitter authentication
    client = getClient()
    
    # Get message to search and number of twits to use in the sentiment analysis
    message = re.sub(' +', ' ', message)
    words = message.split(" ")
    keywords = words[1:]
    keywords = ' '.join(keywords)

    
    # Tweets search
    # Twitter will automatically sample the last 7 days of data. 
    tweets = client.search_recent_tweets(query = keywords, max_results = 100, sort_order = "relevancy").data
    positive = 0
    negative = 0
    neutral = 0
    polarity = 0
    tweet_list = []
    neutral_list = []
    negative_list = []
    positive_list = []
    
    for tweet in tweets:
 
        tweet_list.append(tweet.text)
        analysis = TextBlob(tweet.text)
        score = SentimentIntensityAnalyzer().polarity_scores(tweet.text)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
        polarity += analysis.sentiment.polarity
        
        if neg > pos:
            negative_list.append(tweet.text)
            negative += 1
            
        elif pos > neg:
            positive_list.append(tweet.text)
            positive += 1
        
        elif pos == neg:
            neutral_list.append(tweet.text)
            neutral += 1
            
    positive = percentage(positive, 100)
    negative = percentage(negative, 100)
    neutral = percentage(neutral, 100)
    polarity = percentage(polarity, 100)
    positive = format(positive, '.1f')
    negative = format(negative, '.1f')
    neutral = format(neutral, '.1f')
    
    # Number of Tweets (Total, Positive, Negative, Neutral)
    tweet_list = pd.DataFrame(tweet_list)
    neutral_list = pd.DataFrame(neutral_list)
    negative_list = pd.DataFrame(negative_list)
    positive_list = pd.DataFrame(positive_list)
    tw_list = pd.DataFrame(tweet_list)
    
    # Cleaning Text (duplicate tweets, RT, Punctuation etc)
    tw_list.drop_duplicates(inplace = True)
    
    tw_list["text"] = tw_list[0]
    # Removing RT, Punctuation, etc
    rt = lambda x: re.sub('RT @\w+: '," ",x)
    #rt = lambda x: re.sub("(@[A-Za-z0–9]+)|([0-9A-Za-z \t])|(\w+:\/\/\S+)"," ",x)
    at = lambda x: re.sub("@[A-Za-z0–9]+", " ", x)
    link = lambda x: re.sub(r'http\S+', ' ', x)
    numbers = lambda x: re.sub("[0-9]+",' ', x)
    punctuation = lambda x: re.sub(r'[^\w\s]', ' ', x)
    
    tw_list["text"] = tw_list.text.map(rt).map(at).map(link).map(numbers).map(punctuation)
    tw_list["text"] = tw_list.text.str.lower()
        
    # Calculating Negative, Positive, Neutral and Compound values
    tw_list[['polarity', 'subjectivity']] = tw_list['text'].apply(lambda Text: pd.Series(TextBlob(Text).sentiment))
    for index, row in tw_list['text'].iteritems():
        score = SentimentIntensityAnalyzer().polarity_scores(row)
        neg = score['neg']
        neu = score['neu']
        pos = score['pos']
        comp = score['compound']
        if neg > pos:
            tw_list.loc[index, 'sentiment'] = "negative"
        elif pos > neg:
            tw_list.loc[index, 'sentiment'] = "positive"
        else:
            tw_list.loc[index, 'sentiment'] = "neutral"
        tw_list.loc[index, 'neg'] = neg
        tw_list.loc[index, 'neu'] = neu
        tw_list.loc[index, 'pos'] = pos
        tw_list.loc[index, 'compound'] = comp
                
    
        
    # Count_values for sentiment
    df = count_values_in_column(tw_list, "sentiment")
    return sentiment_format(df)
        
        
    




######################
# BOT MESSAGES
######################

# Help bot message
@bot.message_handler(commands = ["help", "ayuda"])
def help(message):
    mes = "*Bienvenido a la ayuda de Wall-E! Aquí se muestran los distintos comandos e interacciones permitidas con el bot.*\n\n"
    mes = mes + " - */help /ayuda:* mensaje de ayuda sobre los comandos de Wall-E.\n"
    mes = mes + " - */hola:* mensaje de saludo en español.\n"
    mes = mes + " - */hello:* mensaje de saludo en inglés.\n"
    mes = mes + " - */bitcoin /btc:* mensaje con el precio del bitcoin.\n"
    mes = mes + " - */sp500:* mensaje con el precio del índice del S&P500.\n"
    mes = mes + " - */nasdaq /nasdaq100:* mensaje con el precio del índice del NASDAQ100.\n"
    mes = mes + " - */ibex:* mensaje con el precio del índice del IBEX35.\n"
    mes = mes + " - */eurostoxx /stoxx:* mensaje con el precio del índice del EUROSTOXX50.\n"
    mes = mes + " - */gold /oro:* mensaje con el precio del oro.\n"
    mes = mes + " - */eurusd /cambio:* mensaje con el valor del cambio de euros a dólares americanos.\n"
    mes = mes + " - */inflacion:* mensaje con el valor de la inflación en España.\n"
    mes = mes + " - */euribor:* mensaje con el valor del euribor.\n"
    mes = mes + " - */markets /active:* mensaje con los 5 mercados más activos a nivel de movimientos.\n"
    mes = mes + " - */gainers /suben:* mensaje con los activos que más están subiendo o ganando porcentualmente.\n"
    mes = mes + " - */losers /bajan:* mensaje con los activos que más están bajando o perdiendo porcentualmente.\n"
    mes = mes + " - */ortega:* mensaje con la cartelera del cine Ortega de Palencia (España).\n"
    mes = mes + " - */avenida:* mensaje con la cartelera del cine Avenida de Palencia (España).\n"
    mes = mes + " - */cines:* mensaje con la cartelera tanto del cine Ortega como del cine Avenida de Palencia (España).\n"
    mes = mes + " - */news:* despliega un menú de botones para elegir la temática de las noticias que se quieren buscar.\n"
    mes = mes + " - *qr <<url>>*: genera un código qr en forma de imagen enlazando con la url indicada.\n"
    mes = mes + " - *yt <<url>>* or *youtube <<url>>*: descarga un vídeo de Youtube en formato .mp4 dada su url.\n"
    mes = mes + " - *sentiment <<word>>* or *sentimiento <<word>>*: realiza un análisis de sentimientos basado en los 100 tweets más relevantes de la última semana que contenga el término o términos indicados en <<word>>.\n\n"
    
    mes = mes + u"\u26A0" + "*NOTA:* toda la información relativa a los mercados y activos está extraída de la web de Yahoo Finance (https://es.finance.yahoo.com/).\n"
    mes = mes + u"\u26A0" + "*NOTA:* algunos de los comandos descritos admiten otras escrituras, pero las mostradas son las más habituales y recomendadas."
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    

# Greeting message in spanish
@bot.message_handler(commands = ["hola", "Hola", "Buenos días", "Buenos dias", "Buenas tardes", "buenas", "Buenas", "Buenas noches"])
def hola(message):
    mes = "Hola! \U0001F603" + lookup("ES")
    bot.send_message(message.chat.id, mes)
    
    
# Greeting message in english
@bot.message_handler(commands = ["hello", "Hello", "Good morning", "good morning", "good evening", "Good evening", "Good afternoon", "good afternoon", "good night", "Good night"])
def hello(message):
    mes = "Hello! \U0001F603" + lookup("GB")
    bot.send_message(message.chat.id, mes)
    

# Bitcoin price message
@bot.message_handler(commands = ["bitcoin", "btc", "Bitcoin"])
def get_btc(message):
    symbol = "BTC-USD"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
# S&P500 index price message
@bot.message_handler(commands = ["sp500", "SP500", "sp", "S&P500", "s&p500"])
def get_sp(message):
    symbol = "^GSPC"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
# NASDAQ100 index price message
@bot.message_handler(commands = ["ndx", "NASDAQ", "nasdaq", "nasdaq100", "NASDAQ100"])
def get_ndx(message):
    symbol = "^NDX"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
# IBEX35 index price message
@bot.message_handler(commands = ["ibex", "IBEX", "IBEX35", "ibex35"])
def get_ibex(message):
    symbol = "^IBEX"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
# EURO STOXX 50 index price message
@bot.message_handler(commands = ["eurostoxx", "EUROSTOXX", "eurostoxx50", "EUROSTOXX50", "stoxx"])
def get_stoxx(message):
    symbol = "^STOXX50E"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
# Gold price message
@bot.message_handler(commands = ["oro", "ORO", "gold", "GOLD"])
def get_gold(message):
    symbol = "GC=F"
    precio = Price(symbol)
    price = precio.get_current_price()
    porcentage = precio.get_current_porcentage()
    mes = precio.format_output(symbol, price, porcentage)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    

    
# EUR-USD (eur-dolar equivalence)
@bot.message_handler(commands = ["eurusd", "EURUSD", "conversion", "cambio", "eurdolar"])
def get_eurusd(message):
    symbol = "EURUSD=X"
    precio = Price(symbol)
    price = precio.get_current_price()
    mes = precio.eurusd_output(price)
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    

    
# Spanish inflation message
@bot.message_handler(commands = ["inflacion", "inflation"])
def get_inflation(message):
    mes = get_spanish_inflation()
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')

# Euribor value message
@bot.message_handler(commands = ["euribor"])
def euribor(message):
    mes = get_euribor()
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
# Most active markets message
@bot.message_handler(commands = ["mercados", "mercados_activos", "markets", "active_markets", "active"])
def get_most_active_markets_mes(message):
    mes = get_most_active_markets()
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
# Top gainers of the day message
@bot.message_handler(commands = ["gainers", "top", "suben", "up"])
def get_top_gainers_actives(message):
    mes = get_top_gainers()
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    

# Top losers of the day message
@bot.message_handler(commands = ["losers", "down", "bajan", "bot"])
def get_top_losers_actives(message):
    mes = get_top_losers()
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
# Ortega cinema (Palencia, Spain) billboard
@bot.message_handler(commands = ["ortega", "Ortega"])
def get_ortega_billboard(message):
    mes = get_cine("https://www.ecartelera.com/cines/420,0,1.html")
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
# Avenida cinema (Palencia, Spain) billboard
@bot.message_handler(commands = ["avenida", "Avenida"])
def get_avenida_billboard(message):
    mes = get_cine("https://www.ecartelera.com/cines/419,0,1.html")
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
# Ortega cinema (Palencia, Spain) billboard and Avenida cinema (Palencia, Spain) billboard
@bot.message_handler(commands = ["cine", "cines", "Cine", "Cines"])
def get_palencia_billboard(message):
    mes = get_cine("https://www.ecartelera.com/cines/420,0,1.html")
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    mes = get_cine("https://www.ecartelera.com/cines/419,0,1.html")
    bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')
    
    
    
    
# Show the different options for the news thematics
@bot.message_handler(commands = ["news"])
def get_news(message):
    markup = types.ReplyKeyboardMarkup(row_width = 2, resize_keyboard = True, one_time_keyboard = True)
    b1 = types.KeyboardButton('Energía')
    b2 = types.KeyboardButton('Banca y seguros')
    b3 = types.KeyboardButton('Construcción')
    b4 = types.KeyboardButton('Telecomunicaciones')
    b5 = types.KeyboardButton('Tecnológicas')
    b6 = types.KeyboardButton('Internet')
    b7 = types.KeyboardButton('Alimentación y consumo')
    b8 = types.KeyboardButton('Motor y automoción')
    b9 = types.KeyboardButton('Turismo y servicios')
    b10 = types.KeyboardButton('Farmacéutica')
    b11 = types.KeyboardButton('Textil')
    b12 = types.KeyboardButton('Audiovisual y medios')
    markup.add(b1, b2, b3, b4, b5, b6, b7, b8, b9, b10, b11, b12)
    bot.send_message(message.chat.id, "Elige la temática de las noticias:", reply_markup = markup)


    
# Message that replies to the user
@bot.message_handler()
def reply(message):
    
    mes = ""
        
        
    # qr generation reply
    if bool(re.match("[\s]*[qQ][rR][\s]+.+", message.text)): # messages of the form qr url (or Qr url...)
        get_qr(message.text)
        bot.send_photo(message.chat.id, photo = open("qr.png", "rb"))
        
        
    # yt video download reply
    elif bool(re.match("[\s]*([yY][tT]|[yY]outube)[\s]+.+", message.text)): # messages of the form yt url (or youtube url...)
        get_yt(message.text)
        bot.send_video(message.chat.id, video = open("video.mp4", "rb"))
        
        
    # Sentiment analysis of a topic based on twitter messages
    elif bool(re.match("[\s]*[sS](entiment|entimiento)[\s]+.+[\s]?", message.text)): # messages of the form sentiment word(s) 
        mes = get_twitter_sentiment_analysis(message.text)
        
  
    
    # Display the link to the Yahoo Finance website for the news of the selected thematic
    if message.text == "Energía":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/energia/")
    elif message.text == "Banca y seguros":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/banca-y-seguros/")
    elif message.text == "Construcción":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/Construccion/")
    elif message.text == "Telecomunicaciones":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/telecomunicaciones/")
    elif message.text == "Tecnológicas":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/Tecnologicas/")
    elif message.text == "Internet":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/internet/")
    elif message.text == "Alimentación y consumo":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/alimentacion-y-consumo/")
    elif message.text == "Motor y automoción":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/motor-y-automocion/")
    elif message.text == "Turismo y servicios":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/turismo y servicios/")
    elif message.text == "Farmacéutica":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/farmaceutica/")
    elif message.text == "Textil":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/textil/")
    elif message.text == "Audiovisual y medios":
        bot.send_message(message.chat.id, "https://es.finance.yahoo.com/industries/audiovisual-y-medios/")
        
    
    # If there is no mes match the bot does not reply the user
    if mes != "":
        bot.send_message(message.chat.id, mes, parse_mode = 'Markdown')

        
        

    

        



# Bot waiting for messages...    
bot.polling()
    
    
    
    


