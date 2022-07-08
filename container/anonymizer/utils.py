import phonenumbers
import spacy
from spacy.language import Language
from spacy_langdetect import LanguageDetector
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import PhoneRecognizer


@Language.factory('language_detector')
def get_lang_detector(nlp, name):
    return LanguageDetector()


def detect_lang(text, nlp):
    # todo try catch
    # nlp = spacy.load("en_core_web_lg", disable=["tagger", "ner"])
    # nlp.add_pipe('language_detector', last=True)
    return nlp(text)._.language["language"]


def load_analyzer_engine():
    LANGUAGES_CONFIG_FILE = "./languages-config.yml"
    configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "no", "model_name": "nb_core_news_lg"},
            {"lang_code": "en", "model_name": "en_core_web_lg"},
        ],
    }

    provider = NlpEngineProvider(nlp_configuration=configuration)
    nlp_engine_with_norwegian = provider.create_engine()
    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    #
    # email_recognizer_en = EmailRecognizer(supported_language="en", context=["email", "mail"])
    # email_recognizer_no = EmailRecognizer(supported_language="no")
    #
    # phone_recognizer_en = PhoneRecognizer(supported_language="en", context=["phone", "number"])
    phone_recognizer_no = PhoneRecognizer(supported_language="no", supported_regions=phonenumbers.SUPPORTED_REGIONS)
    #
    registry = RecognizerRegistry()
    registry.load_predefined_recognizers(
        nlp_engine=nlp_engine_with_norwegian, languages=["en", "no"]
    )
    #
    # # Add recognizers to registry
    # registry.add_recognizer(email_recognizer_en)
    # registry.add_recognizer(email_recognizer_no)
    # registry.add_recognizer(phone_recognizer_en)
    registry.add_recognizer(phone_recognizer_no)

    # Pass the created NLP engine and supported_languages to the AnalyzerEngine
    analyzer = AnalyzerEngine(
        registry=registry,
        nlp_engine=nlp_engine_with_norwegian, supported_languages=["en", "no"]
    )

    return analyzer
