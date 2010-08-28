import cgi
import urllib
import base64

from google.appengine.api import oauth
from oauthtwitter import OAuthApi
from google.appengine.api import urlfetch
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from datetime import datetime
from datetime import timedelta

class Weatherbot(db.Model):
    username = db.StringProperty()
    password = db.StringProperty()
    token = db.StringProperty()
    tokensecret = db.StringProperty()
    zipcode = db.StringProperty()
    wundurl = db.StringProperty()
    lastforecast = db.StringProperty()
    lastwarning = db.StringProperty()
    lastupdate = db.DateTimeProperty(auto_now = True)


class Update(webapp.RequestHandler):
    def get(self):
        botlist = db.GqlQuery('SELECT * FROM Weatherbot ORDER BY zipcode ASC')
        
        failed = False

        consumer_key = "GAd0rbRb34yGGLpcybxBA" 
        consumer_secret = "KJqAgBDNXXJ39zwczPJdYIy0eUydeAeb3DjQwGNtw"  

        for bot in botlist:
            feed = urlfetch.fetch(bot.wundurl)
            tweet = self.get_forecast(feed)
            self.response.out.write(tweet + "<br />")
            if tweet != bot.lastforecast:
                twitter = OAuthApi(consumer_key, consumer_secret, bot.token, bot.tokensecret)
                user_timeline = twitter.UpdateStatus(tweet)                    
                bot.lastforecast = tweet
                bot.lastupdate = datetime.now()
            tweet = self.get_warning(feed)
            self.response.out.write(tweet + "<br />")
            if len(tweet) > 0 and tweet != bot.lastwarning:
                twitter = OAuthApi(consumer_key, consumer_secret, bot.token, bot.tokensecret)
                user_timeline = twitter.UpdateStatus(tweet)                    
                bot.lastwarning = tweet
                bot.lastupdate = datetime.now()
                
            bot.put()
            
        if len(self.request.get('debug')) == 0:
            self.redirect('/')            

    def get_forecast(self, feed):
        for line in feed.content.splitlines():
            if line.startswith('DESCRIPTION:'):
                tweet = line.replace('DESCRIPTION:', '').replace('\\n', '').strip()
                if len(tweet) > 140:
                    return tweet[0:137] + "..."
                else:
                    return tweet
                
    def get_warning(self, feed):
        url = str('')
        for line in feed.content.splitlines():
            if line.startswith('URL:'):
                url = line.replace('URL:', '').replace('\\n', '').strip()
                break
        warning = urlfetch.fetch(url)
        
        i = 0
        data = warning.content.splitlines()
        tweet = str('')
        for line in data:
            if line.strip() == '<div class="red b">':
                j = i
                while data[j + 1].strip() != "</div>":
                    tweet = tweet + data[i + 1].replace('<div>', '').replace('</div>', '').replace('..', '').strip() + " "
                    j = j + 1
                
                break
            else:
                if line.strip().startswith('<div class="red b">'):
                    tweet = data[i + 1].replace('<div>', '').replace('</div>', '').replace('..', '').strip() + " "
                    break

            i = i + 1
        
        tweet = tweet.strip()
        
        if len(tweet) > 140:
            return tweet[0:137] + "..."
        else:
            return tweet
        return str('')


class Home(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html>
<head>
<title>tweatherbot</title>
<style>
  a { color: #3784FF; }
</style>
</head>
<body style="font-family: Arial; padding: 30px;">
<table>
<tr>
  <td>
    <img src="http://code.google.com/p/tweatherbot/logo?cct=1275613276" alt="Logo" style="padding-right: 3px;"> 
  </td>
  <td valign="bottom">
    <span style="font-weight: bold; font-size: 26px;">tweatherbot</span>
    <p style="font-size: 13px; font-style: italic; padding: 0px 0px 1px 0px; margin: 0px;">Local weather reports delivered throughout the day on Twitter!</p>
  </td>
</tr>
</table>
<br />
<br />
<br />
<div>
        """) 
        
        for bot in db.GqlQuery('SELECT * FROM Weatherbot ORDER BY zipcode ASC'):
            self.response.out.write('<a target="_blank" href="http://www.twitter.com/%s">@%s</a>&nbsp;' % (bot.username, bot.username))
            self.response.out.write(bot.lastforecast)
            self.response.out.write('<br />')
            self.response.out.write('<p style="font-size: 13px; font-style: italic; color: #aaaaaa; margin: 0px; padding: 6px 0px 0px 0px;">Published %s</p>' % (bot.lastupdate - timedelta(hours=5)).strftime("%I:%M %p on %b %d"))
            self.response.out.write('<br />')
                  
        self.response.out.write("""
</div>
<br />
<br />
<input type="button" value="Update Forecasts" onClick="location.href='update';" />
        """) 
        
        self.response.out.write('<i style="font-size: 13px;">Last updated %s</i>' % (db.GqlQuery('SELECT * FROM Weatherbot ORDER BY lastupdate DESC LIMIT 1')[0].lastupdate - timedelta(hours=5)).strftime("%I:%M %p on %b %d"))
                  
        self.response.out.write("""
<br />
<br />
<br />
<span style="font-size: 13px;">Copyright &copy; 2010 McCormick Technologies LLC. All Rights Reserved.</span>
<br />
<br />
<img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" />
</body>
</html>
        """)


class Insert(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html>
<head>
<title>tweatherbot</title>
<style>
  a { color: #3784FF; }
</style>
</head>
<body style="font-family: Arial; padding: 30px;">
<table>
<tr>
  <td>
    <img src="http://code.google.com/p/tweatherbot/logo?cct=1275613276" alt="Logo" style="padding-right: 3px;"> 
  </td>
  <td valign="bottom">
    <span style="font-weight: bold; font-size: 26px;">tweatherbot</span>
    <p style="font-size: 13px; font-style: italic; padding: 0px 0px 1px 0px; margin: 0px;">Local weather reports delivered throughout the day on Twitter!</p>
  </td>
</tr>
</table>
<br />
<br />
<br />
<i>Enter the details for the new Weatherbot account below.</i>
<br />
<br />
<form method="post" action="insert">
    <table>
    <tr>
    <td>Twitter Username: </td>
    <td><input type="text" name="username" /></td>
    </tr>
    <tr>
    <td>Twitter Password: </td>
    <td><input type="text" name="password" /></td>
    </tr>
    <tr>
    <td>Wunderground Feed: </td>
    <td><input type="text" name="wundurl" /></td>
    </tr>
    <tr>
    <td>Zip Code: </td>
    <td><input type="text" name="zipcode" /></td>
    </tr>
    </table>
    <br />
    <input type="submit" value="Insert" />
</form>
<br />
<br />
<br />
<span style="font-size: 13px;">Copyright &copy; 2010 McCormick Technologies LLC. All Rights Reserved.</span>
<br />
<br />
<img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" />
</body>
</html>
        """)

    def post(self):
        twitter = OAuthApi(CONSUMER_KEY, CONSUMER_SECRET)
        request_token = twitter.getRequestToken() 

        self.redirect('/')


class Broadcast(webapp.RequestHandler):
    def get(self):
        self.response.out.write("""
<html>
<head>
<title>tweatherbot</title>
<style>
  a { color: #3784FF; }
</style>
</head>
<body style="font-family: Arial; padding: 30px;">
<table>
<tr>
  <td>
    <img src="http://code.google.com/p/tweatherbot/logo?cct=1275613276" alt="Logo" style="padding-right: 3px;"> 
  </td>
  <td valign="bottom">
    <span style="font-weight: bold; font-size: 26px;">tweatherbot</span>
    <p style="font-size: 13px; font-style: italic; padding: 0px 0px 1px 0px; margin: 0px;">Local weather reports delivered throughout the day on Twitter!</p>
  </td>
</tr>
</table>
<br />
<br />
<br />
<i>Enter the details for the Tweet you would like to broadcast to all Weatherbots. </i>
<br />
<br />
<form method="post" action="broadcast">
    <table>
    <tr>
    <td>Message: </td>
    </tr>
    <tr>
    <td><textarea name="message" cols="40" rows="2"></textarea></td>
    </tr>
    </table>
    <br />
    <span style="color: red;">Warning: Please double-check your message. There is no undo for the broadcast feature!</span>
    <br /><br />
    <input type="submit" value="Broadcast" />
</form>
<br />
<br />
<br />
<span style="font-size: 13px;">Copyright &copy; 2010 McCormick Technologies LLC. All Rights Reserved.</span>
<br />
<br />
<img src="http://code.google.com/appengine/images/appengine-silver-120x30.gif" alt="Powered by Google App Engine" />
</body>
</html>
        """)

    def post(self):
        botlist = db.GqlQuery('SELECT * FROM Weatherbot ORDER BY zipcode ASC')

        consumer_key = "GAd0rbRb34yGGLpcybxBA" 
        consumer_secret = "KJqAgBDNXXJ39zwczPJdYIy0eUydeAeb3DjQwGNtw"  

        for bot in botlist:
            tweet = self.request.get('message')
            twitter = OAuthApi(consumer_key, consumer_secret, bot.token, bot.tokensecret)
            user_timeline = twitter.UpdateStatus(tweet)

        self.redirect('/')


def main():
    application = webapp.WSGIApplication([('/broadcast', Broadcast),
                                          ('/insert', Insert),
                                          ('/update', Update),
                                          ('/', Home)], debug=True)
    run_wsgi_app(application)

if __name__ == "__main__":
    main()