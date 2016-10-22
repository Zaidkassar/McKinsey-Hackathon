from flask import Flask, request, redirect
from twilio import twiml

app = Flask(__name__)

numbers = []

@app.route("/", methods=['GET', 'POST'])
def response():
    resp = twilio.twiml.Response()
    from_number = request.values.get('From', None)
    body = request.values.get('Body', None).lower()
    if body == "updates":
        if from_number not in numbers:
            numbers.append(from_number)
            resp.message('You have been signed up for updates')
        else:
            resp.message('You are already signed up for updates')
    elif body == "cancel":
        if from_number not in numbers:
            resp.message('You are not regsitered for updates')
        else:
            numbers.remove(from_number)
            resp.message('You have been removed from the update list')
    elif body == 'vaccines':
        resp.message = ("Vaccines Available:\n Fill this")
    elif body == "help":
        resp.message('Commands:\n "updates" to recieve updates on vaccines\n "vaccines" for available vaccines\n"cancel" to stop updates')
    else:
        resp.message('Command not recognized, message "help" for commands')

    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
