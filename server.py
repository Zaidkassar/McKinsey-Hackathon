from flask import Flask, request, redirect
from twilio import twiml
import os

app = Flask(__name__)

numbers = []
vaccines = ['Hand, Foot and Mouth Disease']
number_values = {}

@app.route('/', methods=['GET', 'POST'])
def response():

    resp = twiml.Response()
    from_number = str(request.values.get('From', None))
    body = request.values.get('Body', None).lower()

    if from_number in number_values and 'state' in number_values[from_number] and number_values[from_number]['state'] == "clinics":
        #GOOGLE API body
        number_values[from_number]['clinics'] = ["RESULT1", "RESULT2", "RESULT3"]
        message = number_values[from_number]['clinics'][number_values[from_number]['index']]
        number_values[from_number]['index'] += 1
        number_values[from_number]['state'] = "clinic result"
    elif from_number in number_values and 'state' in number_values[from_number] and number_values[from_number]['state'] == "clinic result" and body == "next":
        message = number_values[from_number]['clinics'][number_values[from_number]['index']]
        number_values[from_number]['index'] += 1
        if number_values[from_number]['index'] >= 3:
            number_values[from_number]['state'] = 'normal'
    elif body == "hello" or body == "hi":
        message = 'Hello! Welcome to VacciNow. Message "commands" to see available commands'
    elif body == "on":
        if from_number not in numbers:
            numbers.append(from_number)
            message = 'You have been signed up for updates. Message "off" to turn updates off'
            if from_number in number_values:
                number_values[from_number]['updates'] = "on"
            else:
                number_values[from_number] = {}
                number_values[from_number]['updates'] = "on"
        else:
            message = 'You are already signed up for updates. Message "off" to turn updates off'
    elif body == "off":
        if from_number not in numbers:
            message = 'You are not regsitered for updates. Message "on" to turn updates on'
        else:
            numbers.remove(from_number)
            message = 'You have been removed from the update list. Message "on" to turn updates on'
            if from_number in number_values:
                number_values[from_number]['updates'] = "off"
            else:
                number_values[from_number] = {}
                number_values[from_number]['updates'] = "off"
    elif body == 'vaccines' or body == 'vaccine':
        number_reccomendations = 0
        message = "Vaccines Recommended:\n"
        for item in vaccines:
            if from_number not in number_values or 'taken' not in number_values[from_number] or item not in number_values[from_number]['taken']:
                message += item +'\n'
                number_reccomendations += 1
        if number_reccomendations == 0:
            message = "You are up to date on all our vaccine reccomendations"
    elif body == 'clinics':
        message = "Please send us your location"
        if from_number in number_values:
            number_values[from_number]['state'] = "clinics"
        else:
            number_values[from_number] = {}
            number_values[from_number]['state'] = "clinics"
            number_values[from_number]['index'] = 0
    elif body == "commands" or body == 'command':
        message ='Commands:\n'
        if from_number in number_values and 'updates' in number_values[from_number] and number_values[from_number]['updates'] == "on":
            message += '"off" to stop updates\n'
        else:
            message += '"on" to recieve updates on vaccines\n'
        message += '"vaccines" for recommended vaccines\n"clinics" for nearby clinics\n"DISEASE NAME off" to mark a vaccine as taken'
    else:
        body = body.split()
        command = body[len(body)-1]
        if  command == "on" or command == "off":
            body.pop()
            body = " ".join(body)
            if body not in map(str.lower, vaccines):
                message = '"' + body + '" is not recognized as a current reccomended disease'
            elif command == "on":
                if from_number in number_values:
                    if 'taken' in number_values[from_number]:
                        if body not in number_values[from_number]['taken']:
                            number_values[from_number]['taken'].append(body)
                            message = body + " has been added to your current vaccines taken"
                        else:
                            message = body + " was previously added to your current vaccines taken"
                    else:
                        number_values[from_number]['taken'] = [body]
                        message = body + " has been added to your current vaccines taken"
                else:
                    number_values[from_number] = {}
                    number_values[from_number]['taken'] = [body]
                    message = body + " has been added to your current vaccines taken"
            elif command == "off":
                if from_number in number_values and 'taken' in number_values[from_number] and body in number_values[from_number]['taken']:
                    number_values[from_number]['taken'].remove(body)
                    message = body + " has been removed from your current vaccines taken"
                else:
                    message = body + " was not one of your current vaccines taken"
        else:
            message = 'Command not recognized, message "commands" for commands'

    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=int(os.environ['PORT']))
