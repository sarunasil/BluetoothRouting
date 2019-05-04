from flask import Flask, request, jsonify, abort
import smtplib
import getpass
import datetime
import logging
from pathlib import Path
from model import get_receivers_emails, get_receivers, get_receiver, delete_receivers, delete_receiver, receiver_email_exists, create_receiver

# logging configuration
LOG_FILE = "/var/log/alarms.log"
Path(LOG_FILE).touch()  # make sure log file is created

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
filehandler = logging.FileHandler(LOG_FILE)
filehandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
filehandler.setFormatter(formatter)
logger.addHandler(filehandler)

# app config. and init.
app = Flask(__name__)


smtp_port = 465
smtp_server = "smtp.gmail.com"
email = input("Email:")
password = getpass.getpass("Password:")

message = """
Received an alarm on {0} UTC
\n
{1}"""


@app.route('/receivers', methods=['POST', 'GET', 'DELETE'])
def api_receivers():

    if request.method == 'GET':
        return jsonify(get_receivers())

    elif request.method == 'DELETE':
        return jsonify(delete_receivers())

    elif request.method == 'POST':
        body = request.json

        if body is None:
            abort(400, "Expecting JSON body.")

        if body.keys() != {"email"}:
            abort(400, "Invalid JSON content.")

        if receiver_email_exists(body["email"]):
            abort(409, "Email receiver already exists.")

        return jsonify(create_receiver(body["email"]))


@app.route('/receivers/<uuid:index>', methods=['GET', 'DELETE'])
def api_receivers_instance(index):

    email_object = get_receiver(index)

    if email_object is None:
        abort(404, "Email receiver with the given ID doesn't exist.")

    if request.method == 'GET':

        return jsonify(email_object)

    elif request.method == 'DELETE':

        return jsonify(delete_receiver(email_object))


@app.route('/alarms', methods=['POST', 'GET'])
def api_alert():

    email_addresses = get_receivers_emails()

    if request.method == 'POST':
        body = request.json

        if body is None:
            abort(400, "Expecting JSON body.")

        if body.keys() != {"msg"}:
            abort(400, "Invalid JSON content.")

        msg = body['msg']

        logger.info("Received alarm with message - {0}, potential receivers - {1}".format(msg, email_addresses))

        logger.warning(msg)

        if len(email_addresses) > 0 and request.args.get("with_email", "true") == "true":
            logger.info("Sending alarm to receivers - {0}".format(email_addresses))
            # send the email acknowledging an alarm
            email_msg = message.format(datetime.datetime.now(), msg)
            server_ssl = smtplib.SMTP_SSL(smtp_server, smtp_port)
            server_ssl.login(email, password)
            server_ssl.sendmail(email, email_addresses, email_msg)
            server_ssl.quit()

        logger.info("----------------------------------------------------------------------------")

        return jsonify({"msg": "Alarm acknowledged."})

    elif request.method == 'GET':

        with open(LOG_FILE) as fh:
            content = fh.read()

        return content


app.run(host='0.0.0.0', port=8080)