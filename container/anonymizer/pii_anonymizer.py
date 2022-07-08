from typing import Optional, List
import phonenumbers

import spacy
from presidio_anonymizer import AnonymizerEngine

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import PhoneRecognizer
try:
    from constants import SUPPORTED_LANG, TAGGED_TEXT_MODE, DETAIL_INFO_MODE, REPLACED_TEXT_MODE
    from utils import detect_lang
except ModuleNotFoundError:
    from container.anonymizer.constants import SUPPORTED_LANG, TAGGED_TEXT_MODE, DETAIL_INFO_MODE, REPLACED_TEXT_MODE
    from container.anonymizer.utils import detect_lang

# entities = ["PHONE_NUMBER", "CREDIT_CARD", "EMAIL_ADDRESS",
#             "IBAN_CODE", "LOCATION", "PERSON", "PHONE_NUMBER",
#             "US_PASSPORT", "US_SSN", "UK_NHS"]


class PiiAnonymizer:
    def __init__(self):
        self.anonymizer = AnonymizerEngine()
        self.analyzer = self._load_analyzer_engine()
        self.nlp = self._nlp()

    @staticmethod
    def _nlp():
        nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner"])
        nlp.add_pipe('language_detector', last=True)
        return nlp

    @staticmethod
    def _load_analyzer_engine():
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

    def anonymize_text(self, text: str, mode: str = TAGGED_TEXT_MODE, entities: Optional[List[str]] = None,
                       lang: str = "en"):
        result = {}
        if lang == "unknown":
            lang = detect_lang(text, self.nlp)
        elif lang not in SUPPORTED_LANG:
            raise ValueError(f"Support for language {lang} is not implemented yet!")
        analyzer_result = self.analyzer.analyze(text=text,
                                                entities=entities,  # detect all predefined entities
                                                language=lang)
        anonymizer_result = self.anonymizer.anonymize(text=text, analyzer_results=analyzer_result)
        if mode == TAGGED_TEXT_MODE:
            result[TAGGED_TEXT_MODE] = anonymizer_result.text
        elif mode == DETAIL_INFO_MODE:
            result[DETAIL_INFO_MODE] = []
            for res in analyzer_result:
                d = res.__dict__.copy()
                d.pop("analysis_explanation")
                d.pop("recognition_metadata")
                d["entity"] = text[res.start:res.end]
                result[DETAIL_INFO_MODE].append(d)
        elif mode == REPLACED_TEXT_MODE:
            raise ValueError(f"Support for {REPLACED_TEXT_MODE} mode is not implemented yet!")
        else:
            raise ValueError(f"Mode {mode} not supported!")

        return result
