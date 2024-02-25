from flask import Flask, redirect, render_template, request, session, url_for, abort, jsonify, render_template_string, send_file
from datetime import datetime
from pytz import timezone
from werkzeug.middleware.proxy_fix import ProxyFix
import app_config
from authlib.integrations.flask_client import OAuth
from warnings import filterwarnings
from functions import get_picture, check_login





filterwarnings('ignore')

app = Flask(__name__)
app.config.from_object(app_config)

tz = timezone('Brazil/East')
year = f'{datetime.now(tz=tz):%Y}'

app.secret_key =  app.config["SECRET_SESSION"]

app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)




# Google
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=app.config["CLIENT_ID_GOOGLE"],
    client_secret=app.config["CLIENT_SECRET_GOOGLE"],
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params={'access_type': 'offline', 'prompt': 'consent'},
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',  
    client_kwargs={'scope': 'openid email profile'},
    jwks_uri = "https://www.googleapis.com/oauth2/v3/certs"
)



# ROUTES

@app.route("/")
def page_home():
    return render_template('index.html', year=year)


@app.route("/login")
def login():

    check_log = check_login(session)

    if check_log: 
        return redirect(url_for("page_protect"))

    google = oauth.create_client('google') 
    redirect_uri = url_for('authorize', _external=True)

    return google.authorize_redirect(redirect_uri)



@app.route('/authorize')
def authorize():

    google = oauth.create_client('google')  
    token = google.authorize_access_token() 
    resp = google.get('userinfo')  
    user_info = resp.json()

    session["access_token"] = token.get("access_token")
    session["refresh_token"] = token.get("refresh_token")

    try:  session['exp'] = token['userinfo']['exp']
    except (KeyError, TypeError):  session['exp'] = None

    try:  session['username'] = token['userinfo']['email']
    except (KeyError, TypeError):  session['username'] = None

    try:  session['sub'] = token['userinfo']['sub']
    except (KeyError, TypeError):  return redirect(url_for("page_home"))

    try:  session['name'] = user_info['name']
    except (KeyError, TypeError):  session['name'] = None

    # Persistent Session
    session.permanent = True

    return redirect(url_for("page_protect"))



@app.route('/protect')
def page_protect():
    check_log = check_login(session)

    if not check_log: return redirect(url_for("page_home"))




    if not 'picture' in session:

        picture = get_picture(session['access_token'])
        session['picture'] = picture
        

    name = session['name'] if 'name' in session else ''



    return render_template('protect.html',picture=session['picture'], name=name)





@app.route('/logout')
def logout():
    
    session.pop('access_token', None)

    try:
        google.revoke_token(session.get('refresh_token')) 
    except: 
        pass

    session.clear()

    return redirect(url_for('page_home'))



if __name__ == '__main__':
     app.run(debug=True)