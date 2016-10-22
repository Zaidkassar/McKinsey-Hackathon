from flask import Flask, request, redirect
from twilio import twiml
import os

print "PORT = " + os.environ['PORT']

app = Flask(__name__)

numbers = []

@app.route('/', methods=['GET', 'POST'])
def response():

    resp = twiml.Response()
    resp.message("Hello, Connor")
    return str(resp)

    resp = twilio.twiml.Response()
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None).lower()
    if body == "updates":
        if from_number not in numbers:
            numbers.append(from_number)
            message = 'You have been signed up for updates'
        else:
            message = 'You are already signed up for updates'
    elif body == "cancel":
        if from_number not in numbers:
            message = 'You are not regsitered for updates'
        else:
            numbers.remove(from_number)
            message = 'You have been removed from the update list'
    elif body == 'vaccines':
        message = ("Vaccines Available:\n Fill this")
    elif body == "help":
        message ='Commands:\n "updates" to recieve updates on vaccines\n "vaccines" for available vaccines\n"cancel" to stop updates'
    else:
        message = 'Command not recognized, message "help" for commands'

    resp.message(message)

    return str(resp)

if __name__ == "__main__":
    app.run(host=0.0.0.0, debug=True, port=int(os.environ['PORT']))
