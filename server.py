from flask import Flask, request, redirect
from twilio import twiml
import os

app = Flask(__name__)

numbers = []
vaccines = ['Hand, Foot and Mouth Disease']
all_vaccines = ['Hand, Foot and Mouth Disease', 'Dengue Fever', 'Measles', 'Acute Viral Hepititis B']

@app.route('/', methods=['GET', 'POST'])
def response():

    resp = twiml.Response()
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None).lower()
    if body == "on":
        if from_number not in numbers:
            numbers.append(from_number)
            message = 'You have been signed up for updates'
        else:
            message = 'You are already signed up for updates'
    elif body == "off":
        if from_number not in numbers:
            message = 'You are not regsitered for updates'
        else:
            numbers.remove(from_number)
            message = 'You have been removed from the update list'
    elif body == 'vaccines' or body == 'vaccine':
        message = "Vaccines Recommended:\n"
        for item in vaccines:
            message += item +'\n'
    elif body == 'vaccines all' or body == 'vaccine all':
        message = "Vaccines Available:\n"
        for item in vaccines_all:
            message += item +'\n'
    elif body == 'clinics':
        message = "WEBSITE URL"
    elif body == 'website':
        message = "WEBSITE URL"
    elif body == "commands" or body == 'command':
        message ='Commands:\n"on" to recieve updates on vaccines\n"vaccines" for recommended vaccines\n"vaccines all" for all vaccines\n"off" to stop updates'
    else:
        message = 'Command not recognized, message "commands" for commands'

    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True, port=int(os.environ['PORT']))
