import json
import flask

from container.anonymizer.pii_anonymizer import PiiAnonymizer

app = flask.Flask(__name__)

pii_anonymizer = PiiAnonymizer()


@app.route("/ping", methods=["GET"])
def ping():
    # Check if the classifier was loaded correctly
    try:
        pii_anonymizer
        status = 200
    except:
        status = 400
    return flask.Response(
        response=json.dumps(" "), status=status, mimetype="application/json"
    )


@app.route("/invocations", methods=["POST"])
def handle_call():
    input_json = flask.request.get_json()
    response = []
    mode = input_json["mode"]
    for text in input_json["input"]:
        result = pii_anonymizer.anonymize_text(
            text=text["text"], mode=mode, lang=text["lang"]
        )
        response.append(result)
    result = {"output": response}
    result = json.dumps({"output": result})
    return flask.Response(response=result, status=200, mimetype="application/json")
