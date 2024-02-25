from datetime import datetime
import base64
import requests
import app_config

# Checked login

def check_login(session):

    if ("access_token" not in  list(session.keys())) or ("exp" not in list(session.keys())) or ('username' not in list(session.keys())):
       return False

    if str(session['exp']) == "None" or str(session["access_token"])  == "None" or str(session["username"])  == "None":
        return False
    
    if not 'username' in session.keys(): return False

    if datetime.timestamp(datetime.now()) > float(session['exp']):
    
        token = refresh_token_google(session["refresh_token"])

        if 'error' in token:
            return False
        
        
        # Salva novos tokens 
        session['access_token'] = token['access_token'] 
        session['exp'] = datetime.now().timestamp() + token['expires_in'] - (60 * 5)

    
    return True



# Refresh Token Google

def refresh_token_google(refresh_token):

    response_token = requests.post("https://accounts.google.com/o/oauth2/token",
                            data= {
                                    'grant_type':'refresh_token',
                                    'refresh_token': refresh_token,
                                    'client_id':app_config.CLIENT_ID_GOOGLE,
                                    'client_secret': app_config.CLIENT_SECRET_GOOGLE,
                                })

    token = response_token.json()

    return token









# Get Image Profile

def get_picture(token): 

    with open(".//static//profile.png", "rb") as file:

        bytes_photo = file.read()

    encode_photo =  base64.b64encode(bytes_photo).decode('utf-8')



    picture = '' 

    
    
    userinfo_response = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {token}"}   
    )

    if userinfo_response.status_code == 200:

        link_picture = userinfo_response.json()["picture"]

        response_picture = requests.get(link_picture, headers={"Authorization": f"Bearer {token}"})

        if response_picture.status_code == 200:

            picture = response_picture.content

            encode_photo =  base64.b64encode(picture).decode('utf-8')


    return encode_photo






