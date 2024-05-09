from django.shortcuts import render
import requests
import datetime

def welcome(request):
    return render(request, 'weather/welcome.html')

def current(request):
    api = 'b2d676e4a3dbbb669dfab6d72c0449a4'
    weatherLink = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    if request.method == "POST":
        city = request.POST['city']
        response = requests.get(weatherLink.format(city, api)).json()
        weatherData = {
            'city': city,
            'country': response['sys']['country'],
            'temperature': round((response['main']['temp'] - 273.15) * 9/5 + 32, 2),
            'feels_like': round((response['main']['feels_like'] - 273.15) * 9/5 + 32, 2),
            'min_temp': round((response['main']['temp_min'] - 273.15) * 9/5 + 32, 2),
            'max_temp': round((response['main']['temp_max'] - 273.15) * 9/5 + 32, 2),
            'pressure': response['main']['pressure'],
            'humidity': response['main']['humidity'],
            'visibility': response['visibility'],
            'wind_speed': response['wind']['speed'],
            'wind_direction': degrees_to_cardinal(response['wind']['deg']),
            'description': response['weather'][0]['description'],
            'icon': response['weather'][0]['icon'],
        }
        context = {
            'weatherData': weatherData,
        }
        return render(request, 'weather/current.html', context)
    return render(request, 'weather/current.html')

def forecast(request):
    api = 'b2d676e4a3dbbb669dfab6d72c0449a4'
    forecastLink = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&exclude=current,minutely,hourly,alerts&appid={}'

    if request.method == "POST":
        city = request.POST['city']

        weatherData, forecastData, city_info = getWeatherForecast(city, api, forecastLink)

        context = {
            'forecastData': forecastData,
            'city_info': city_info,  # Add city_info to context
        }

        return render(request, 'weather/forecast.html', context)

    return render(request, 'weather/forecast.html')

def precipitation(request):
    api = 'b2d676e4a3dbbb669dfab6d72c0449a4'
    forecastLink = 'https://api.openweathermap.org/data/2.5/forecast?lat={}&lon={}&appid={}'

    if request.method == "POST":
        city = request.POST['city']
        weatherLink = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
        weatherResponse = requests.get(weatherLink.format(city, api)).json()
        lat, lon = weatherResponse['coord']['lat'], weatherResponse['coord']['lon']

        forecastResponse = requests.get(forecastLink.format(lat, lon, api)).json()
        precipitationData = {}

        for hourData in forecastResponse['list']:
            time = datetime.datetime.fromtimestamp(hourData['dt'])
            day_key = time.strftime('%A, %B %d')

            if day_key not in precipitationData:
                precipitationData[day_key] = []

            if len(precipitationData[day_key]) < 8:  # Limiting data to 8 entries per day for 3-hour intervals
                precipitationData[day_key].append({
                    'time': time.strftime('%I:%M %p'),
                    'precipitation': hourData.get('rain', {}).get('3h', 0),
                    'snow': hourData.get('snow', {}).get('3h', 0),
                    'cloudiness': hourData.get('clouds', {}).get('all', 0),
                    'humidity': hourData['main']['humidity'],
                    'wind_speed': hourData['wind']['speed'],
                    'wind_direction': degrees_to_cardinal(hourData['wind']['deg']),
                    'probability_of_precipitation': hourData.get('pop', 0) * 100,
                })

        city_info = {
            'name': weatherResponse['name'],
            'country': weatherResponse['sys']['country']
        }

        context = {
            'city': city,
            'precipitationData': precipitationData,
            'city_info': city_info,
        }

        return render(request, 'weather/precipitation.html', context)

    return render(request, 'weather/precipitation.html')


def degrees_to_cardinal(d):
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    ix = int((d + 11.25)/22.5 - 0.02)
    return dirs[ix % 16]


def getWeatherForecast(city, api, forecastLink):
    weatherLink = 'https://api.openweathermap.org/data/2.5/weather?q={}&appid={}'
    response = requests.get(weatherLink.format(city, api)).json()
    lat, lon = response['coord']['lat'], response['coord']['lon']

    weatherData = {
        'city': city,
        'temperature': round((response['main']['temp'] - 273.15) * 9/5 + 32, 2),
        'description': response['weather'][0]['description'],
        'icon': response['weather'][0]['icon'],
    }

    forecastRequest = requests.get(forecastLink.format(lat, lon, api)).json()
    forecastData = {}

    for dailyData in forecastRequest['list'][:40]:
        dayOfWeek = datetime.datetime.fromtimestamp(dailyData['dt']).strftime('%A')
        if dayOfWeek not in forecastData:
            forecastData[dayOfWeek] = []
        
        forecastData[dayOfWeek].append({
            'date': datetime.datetime.fromtimestamp(dailyData['dt']).date(),
            'day': dayOfWeek,
            'time': datetime.datetime.fromtimestamp(dailyData['dt']).strftime('%I:%M %p'),
            'temp': round((dailyData['main']['temp'] - 273.15) * 9/5 + 32, 2),
            'min_temp': round((dailyData['main']['temp_min'] - 273.15) * 9/5 + 32, 2),
            'description': dailyData['weather'][0]['description'],
            'icon': dailyData['weather'][0]['icon'],
        });


    city_info = {
        'name': response['name'],
        'country': response['sys']['country']
    }

    return weatherData, forecastData, city_info