from flask import Flask, request, redirect
from twilio import twiml
from twilio.rest import TwilioRestClient
import os
import pandas as pd
import math
import googlemaps

def getDistanceLatLon(lat1, lon1, lat2, lon2):
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2) * math.sin(dlat/2) + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)*math.sin(dlon/2)
    c = 2 * math.atan2(math.sqrt(a),math.sqrt(1-a))
    dist = R*c
    return dist

def getClinics(user_address):
    geocode_result = gmaps.geocode(user_address)
    if not geocode_result:
        return []
    df = pd.read_csv("clinic_geodata.csv")
    latitude = geocode_result[0]['geometry']
    longitude = geocode_result[0]['geometry']
    if 'location' in latitude:
        latitude = latitude['location']['lat']
        longitude = longitude['location']['lng']
    else:
        latitude = latitude['bounds']['northeast']['lat']
        longitude = longitude['bounds']['northeast']['lng']

    df['dist'] = df.apply(lambda x:getDistanceLatLon(x['LON'],x['LAT'],latitude, longitude),axis=1)
    df.sort_values(by=['dist'],ascending=1,inplace=True)
    df.drop(['LAT','LON','dist'],axis=1,inplace=True)
    clinics = []
    for i in range(3):
        clinics.append(str(df.iloc[i, 0]) + "\n\nLocation: " + str(df.iloc[i, 1]) + "\n\nPhone number: " + str(df.iloc[i, 2]))
    return clinics

app = Flask(__name__)

numbers = []
vaccines = ['Hand, Foot and Mouth Disease']
number_values = {}
ACCOUNT_SID = #Removed
AUTH_TOKEN = #Removed
gmaps = googlemaps.Client(key=#Removed)
client = TwilioRestClient(ACCOUNT_SID, AUTH_TOKEN)

@app.route('/notify', methods=["GET", "POST"])
def notifications():
    for number in numbers:
        from_number = str(number)
        number_recommendations = 0
        message = "Vaccines Recommended:\n\n"
        for item in vaccines:
            if from_number not in number_values or 'taken' not in number_values[from_number] or item.lower() not in number_values[from_number]['taken']:
                message += item +'\n\n'
                number_recommendations += 1
        message += 'Message "[insert disease name] OFF" for vaccines taken\n\nMessage "CLINICS" for nearby clinics'
        if number_recommendations != 0:
            client.messages.create(
                to=number,
                from_="+12898132193",
                body=message
            )
    return 'Sent'

@app.route('/thanks', methods=["GET", "POST"])
def thanks():
    for number in numbers:
        from_number = str(number)
        client.messages.create(
            to=number,
            from_="+12898132193",
            body="Thank you for listening to our presentation"
        )
    return 'Sent'

@app.route('/', methods=['GET', 'POST'])
def response():
    resp = twiml.Response()
    insert_number = request.values.get('From', None)
    from_number = str(insert_number)
    body = request.values.get('Body', None).lower()

    if from_number in number_values and 'state' in number_values[from_number] and number_values[from_number]['state'] == "clinics":
        number_values[from_number]['state'] = "normal"
        number_values[from_number]['clinics'] = getClinics(body)
        if number_values[from_number]['clinics'] == []:
            message = 'Address, "' + body + '" not found'
            number_values[from_number]['state'] = "normal"
        else:
            message = number_values[from_number]['clinics'][number_values[from_number]['index']] + '\n\nMessage "NEXT" for another nearby clinic'
            number_values[from_number]['index'] += 1
            number_values[from_number]['state'] = "clinic result"
    elif from_number in number_values and 'state' in number_values[from_number] and number_values[from_number]['state'] == "clinic result" and body.strip() == "next":
        message = number_values[from_number]['clinics'][number_values[from_number]['index']]
        number_values[from_number]['index'] += 1
        if number_values[from_number]['index'] < 3:
            message += '\n\nMessage "NEXT" for another nearby clinic'
        else:
            number_values[from_number]['state'] = 'normal'
    elif body.strip() == "hello" or body.strip() == "hi":
        message = 'Hello! Welcome to VacciNow. Message "COMMANDS" to see available commands'
    elif body.strip() == "on":
        if insert_number not in numbers:
            numbers.append(insert_number)
            message = 'You have been signed up for updates. Message "OFF" to turn updates off'
            if from_number in number_values:
                number_values[from_number]['updates'] = "on"
            else:
                number_values[from_number] = {}
                number_values[from_number]['updates'] = "on"
        else:
            message = 'You are already signed up for updates. Message "OFF" to turn updates off'
    elif body.strip() == "off":
        if insert_number not in numbers:
            message = 'You are not regsitered for updates. Message "ON" to turn updates on'
        else:
            numbers.remove(insert_number)
            message = 'You have been removed from the update list. Message "ON" to turn updates on'
            if from_number in number_values:
                number_values[from_number]['updates'] = "off"
            else:
                number_values[from_number] = {}
                number_values[from_number]['updates'] = "off"
    elif body.strip() == 'outbreak' or body.strip() == 'outbreaks':
        number_recommendations = 0
        message = "Vaccines Recommended:\n\n"
        for item in vaccines:
            if from_number not in number_values or 'taken' not in number_values[from_number] or item.lower() not in number_values[from_number]['taken']:
                message += item +'\n\n'
                number_recommendations += 1
        if number_recommendations == 0:
            message = "You are up to date on all our vaccine recommendations"
        else:
            message += 'Message "CLINICS" for nearby clinics'
    elif body.strip() == 'clinics' or body.strip() == 'clinic':
        message = "Please send us your location"
        if from_number in number_values:
            number_values[from_number]['state'] = "clinics"
            number_values[from_number]['index'] = 0
        else:
            number_values[from_number] = {}
            number_values[from_number]['state'] = "clinics"
            number_values[from_number]['index'] = 0
    elif body.strip() == "commands" or body.strip() == 'command':
        message ='Text Commands:\n\n"OUTBREAK" for recommended vaccines\n\n"CLINICS" for nearby clinics\n\n'
        if from_number in number_values and 'updates' in number_values[from_number] and number_values[from_number]['updates'] == "on":
            message += '"OFF" to stop updates on vaccines\n\n'
        else:
            message += '"ON" to receive updates on vaccines\n\n'
        message += '"[insert disease name] ON" or "[insert disease name] OFF" to mark a vaccine as taken'
    else:
        body = body.split()
        command = body[len(body)-1]
        if  command == "on" or command == "off":
            body.pop()
            body = " ".join(body)
            if body not in map(str.lower, vaccines):
                message = '"' + body + '" is not recognized as a current recommended disease'
            elif command == "off":
                if from_number in number_values:
                    if 'taken' in number_values[from_number]:
                        if body not in number_values[from_number]['taken']:
                            number_values[from_number]['taken'].append(body)
                            message = '"' + body + '" has been added to your current vaccines taken'
                        else:
                            message = '"' + body + '" was previously added to your current vaccines taken'
                    else:
                        number_values[from_number]['taken'] = [body]
                        message = body + " has been added to your current vaccines taken"
                else:
                    number_values[from_number] = {}
                    number_values[from_number]['taken'] = [body]
                    message = '"' + body + '" has been added to your current vaccines taken'
            elif command == "on":
                if from_number in number_values and 'taken' in number_values[from_number] and body in number_values[from_number]['taken']:
                    number_values[from_number]['taken'].remove(body)
                    message = '"' + body + '" has been removed from your current vaccines taken'
                else:
                    message = '"' + body + '" was not one of your current vaccines taken'
        else:
            message = 'Command not recognized, message "COMMANDS" for commands'

    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=int(os.environ['PORT']))
