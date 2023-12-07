import requests
import streamlit
from gtts import gTTS
import geocoder
import os
from dotenv import load_dotenv

def load_api_key():
    load_dotenv()
    api_key = os.getenv("API_KEY")
    if api_key is None:
        raise ValueError("API_KEY not found in the environment variables")
    return api_key

def get_location():
    location = geocoder.ip('me')
    return location.latlng

def fetch_weather_data(api_key, user_location):
    url = 'https://api.tomorrow.io/v4/timelines'
    params = {
        'location': f'{user_location[0]},{user_location[1]}',
        'fields': 'rainIntensity',
        'timesteps': '1d',
        'units': 'metric',
        'apikey': api_key
    }
    headers = {'Accept-Encoding': 'gzip'}
    response = requests.get(url, params=params, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

def check_rain(data):
    if data:
        rainpred = data['data']['timelines'][0]['intervals'][0]['values']['rainIntensity']
        if rainpred == 0:
            text = "There is No rain today"
        elif rainpred > 0:
            text = "There is a chance of rain today. Get the wipers ready."
    return text

def main():
    api_key = load_api_key()
    user_location = get_location()
    weather_data = fetch_weather_data(api_key, user_location)
    rainpred = check_rain(weather_data)

if __name__ == "__main__":
    main()