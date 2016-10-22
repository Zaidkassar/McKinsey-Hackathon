from flask import Flask, request, redirect
from twilio import twiml

app = Flask(__name__)

numbers = []

@app.route("/", methods=['GET', 'POST'])
def response():

    twilio_account_sid = app.flask_app.config['ACa21cfc418e446b328b2a6e652e885cac']
    twilio_auth_token = app.flask_app.config['d67465f7552e7b382b5c6a9e30dc6ded']
    twilio_number = app.flask_app.config['+12898132193']

    client = Client(twilio_account_sid, twilio_auth_token)

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

    client.messages.create(body=message, to=from_number, from_=twilio_number)

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
