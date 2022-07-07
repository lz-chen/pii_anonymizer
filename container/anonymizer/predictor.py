import json
from typing import Optional, List

import flask
from presidio_analyzer import AnalyzerEngine
from presidio_anonymizer import AnonymizerEngine

TAGGED_TEXT_MODE = "tagged_text"
DETAIL_INFO_MODE = "detailed_info"
REPLACED_TEXT_MODE = "replaced_text"

analyzer = AnalyzerEngine()
anonymizer = AnonymizerEngine()

# entities = ["PHONE_NUMBER", "CREDIT_CARD", "EMAIL_ADDRESS",
#             "IBAN_CODE", "LOCATION", "PERSON", "PHONE_NUMBER",
#             "US_PASSPORT", "US_SSN", "UK_NHS"]

app = flask.Flask(__name__)


def anonymize_text(text: str, mode: str = "tag", entities: Optional[List[str]] = None, lang: str = "en"):
    result = {}
    analyzer_result = analyzer.analyze(text=text,
                                       entities=entities,  # detect all predefined entities
                                       language=lang)
    anonymizer_result = anonymizer.anonymize(text=text, analyzer_results=analyzer_result)
    if mode == TAGGED_TEXT_MODE:
        result[TAGGED_TEXT_MODE] = anonymizer_result.text
    elif mode == DETAIL_INFO_MODE:
        for res in analyzer_result:
            d = res.__dict__.copy()
            d.pop("analysis_explanation")
            d.pop("recognition_metadata")
            d["entity"] = text[res.start:res.end]
            result[DETAIL_INFO_MODE] = d
    elif mode == REPLACED_TEXT_MODE:
        raise NotImplementedError
    else:
        raise ValueError("Mode not supported !!!")

    return result


@app.route('/ping', methods=['GET'])
def ping():
    # Check if the classifier was loaded correctly
    try:
        analyzer
        status = 200
    except:
        status = 400
    return flask.Response(response=json.dumps(' '), status=status, mimetype='application/json')


@app.route('/invocations', methods=['POST'])
def handle_call():
    input_json = flask.request.get_json()
    response = []
    for text in input_json["input"]:
        result = anonymize_text(text=text["text"], mode=text["mode"])
        response.append(result)
    result = {'output': response}
    result = json.dumps({"output": result})
    return flask.Response(response=result, status=200, mimetype='application/json')
