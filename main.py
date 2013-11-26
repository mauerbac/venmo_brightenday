from flask import Flask, request, redirect, session
from constants import CONSUMER_ID, CONSUMER_SECRET, APP_SECRET
import psycopg2
import os
import psycopg2
import urlparse
import requests

app = Flask(__name__)
# comment out when you're done testing
app.debug = True
app.secret_key = APP_SECRET

@app.route('/')
def index():
    if session.get('venmo_token'):
        return 'Your Venmo token is %s' % session.get('venmo_token')
    else:
        return redirect('https://api.venmo.com/oauth/authorize?client_id=%s&scope=make_payments,access_profile,access_email,access_phone&response_type=code' % CONSUMER_ID)

@app.route('/oauth-authorized')
def oauth_authorized():
    #connect to DB 
    import os
    import psycopg2
    import urlparse

    AUTHORIZATION_CODE = request.args.get('code')
    code= AUTHORIZATION_CODE
    print (type(code))
    print (code)
    data = {
        "client_id":CONSUMER_ID,
        "client_secret":CONSUMER_SECRET,
        "code":AUTHORIZATION_CODE
        }
    url = "https://api.venmo.com/oauth/access_token"
    response = requests.post(url, data)
    response_dict = response.json()



    #the current users access token
    access_token = response_dict.get('access_token')
    user = response_dict.get('user')


    session['venmo_token'] = access_token


    #session['venmo_username'] = user['username']

    name = user['name']
    email = user['email']
    phone= user['phone'] 
    print "test"
    print name
    print email
    print phone
    response= enterUser(name, email, phone, code)
    return response

def enterUser(name, email, phone, code):
    #connect to DB
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
    print type(phone)
    phone = int(phone)
    cur = conn.cursor()

    #check if already a user
    cur.execute("Select id from users where phone = %s ;" , [phone])
    test= int(cur.rowcount)
    print "the number of rows" + str(test)

    if test > 1:
        print "we have aleady registered" + name
        cur.close()
        conn.commit()
        conn.close()
        return "You have already registered " + name
    else:
        cur.execute("INSERT INTO users (name, email, phone, code) VALUES (%s, %s,%s, %s)",(name,email, phone, code));
        cur.close()
        conn.commit()
        conn.close()
        return "You are now registered and entered into the DB " + name


if __name__ == '__main__':
    app.run()