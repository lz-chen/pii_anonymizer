from typing import Optional, List
import phonenumbers

import spacy
from presidio_anonymizer import AnonymizerEngine

from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_analyzer import AnalyzerEngine, RecognizerRegistry
from presidio_analyzer.predefined_recognizers import PhoneRecognizer
from spacy import Language

try:
    from constants import (
        SUPPORTED_LANG,
        TAGGED_TEXT_MODE,
        DETAIL_INFO_MODE,
        REPLACED_TEXT_MODE,
    )
    from utils import detect_lang
except ModuleNotFoundError:
    from container.anonymizer.constants import (
        SUPPORTED_LANG,
        TAGGED_TEXT_MODE,
        DETAIL_INFO_MODE,
        REPLACED_TEXT_MODE,
    )
    from container.anonymizer.utils import detect_lang

# entities = ["PHONE_NUMBER", "CREDIT_CARD", "EMAIL_ADDRESS",
#             "IBAN_CODE", "LOCATION", "PERSON", "PHONE_NUMBER",
#             "US_PASSPORT", "US_SSN", "UK_NHS"]


class PiiAnonymizer:
    LANGUAGES_CONFIG_FILE = "./languages-config.yml"
    SUPPORTED_LANG = ["en", "no"]

    def __init__(self):
        self.anonymizer = AnonymizerEngine()
        self.analyzer = self._load_analyzer_engine()

    @staticmethod
    def _nlp() -> Language:
        """
        Load the en_core_web_sm from spacy and create
        a pipeline for language detection
        :return:
        """
        nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner"])
        nlp.add_pipe("language_detector", last=True)
        return nlp

    @staticmethod
    def _nlp_config():
        """
        Configuration for Presidio nlp engine provider
        :return: configuration dictionary
        """
        return {
            "nlp_engine_name": "spacy",
            "models": [
                {"lang_code": "no", "model_name": "nb_core_news_lg"},
                {"lang_code": "en", "model_name": "en_core_web_lg"},
            ],
        }

    @staticmethod
    def _load_analyzer_engine() -> AnalyzerEngine:
        """
        Load Presidio analyzer engine for processing. In addition to predefined recognizers,
        add a PhoneRecognizer for Norwegian
        :return:
        """
        provider = NlpEngineProvider(nlp_configuration=PiiAnonymizer._nlp_config())
        nlp_engine_with_norwegian = provider.create_engine()
        # need to change supported_regions for NO phone number
        phone_recognizer_no = PhoneRecognizer(
            supported_language="no", supported_regions=phonenumbers.SUPPORTED_REGIONS
        )
        registry = RecognizerRegistry()
        registry.load_predefined_recognizers(
            nlp_engine=nlp_engine_with_norwegian, languages=SUPPORTED_LANG
        )

        registry.add_recognizer(phone_recognizer_no)

        # Pass the created NLP engine and supported_languages to the AnalyzerEngine
        analyzer = AnalyzerEngine(
            registry=registry,
            nlp_engine=nlp_engine_with_norwegian,
            supported_languages=SUPPORTED_LANG,
        )
        return analyzer

    def anonymize_text(
        self,
        text: str,
        mode: str = TAGGED_TEXT_MODE,
        entities: Optional[List[str]] = None,
        lang: str = "en",
    ) -> dict:
        """
        Anonymize text according to specified mode and entities
        :param text: text to anonymize
        :param mode: can be "tagged_text", "detailed_info" or "replaced_text". tagged_text mode
        will output text with PII replaced by tags such as <PERSON>, <PHONE_NUMBER> ect;
        detailed_info mode will output a dictionary per PII which contains the start index, end
        index, entity type and entity itself; replaced_text mode will output text with PII replace
        by a random entity of the same type (currently not implemented)
        :param entities: list of entity to detect and anonymize, if it's None, detect all enties
        supported by Presidio https://microsoft.github.io/presidio/supported_entities/
        :param lang: language indicator of the text, if it's "unknown", the spacy language
        detector is used to detect language, currently only anonymize data in English and
        Norwegian are supported
        :return: anonymizer result
        """
        result = {}
        if lang == "unknown":
            nlp = self._nlp()
            lang = detect_lang(text, nlp)
            if lang not in SUPPORTED_LANG:
                raise ValueError(f"Support for language {lang} is not implemented yet!")
        elif lang not in SUPPORTED_LANG:
            raise ValueError(f"Support for language {lang} is not implemented yet!")
        analyzer_result = self.analyzer.analyze(
            text=text,
            entities=entities,
            language=lang,
        )
        anonymizer_result = self.anonymizer.anonymize(
            text=text, analyzer_results=analyzer_result
        )
        if mode == TAGGED_TEXT_MODE:
            result[TAGGED_TEXT_MODE] = anonymizer_result.text
        elif mode == DETAIL_INFO_MODE:
            result[DETAIL_INFO_MODE] = []
            for res in analyzer_result:
                d = res.__dict__.copy()
                d.pop("analysis_explanation")
                d.pop("recognition_metadata")
                d["entity"] = text[res.start : res.end]
                result[DETAIL_INFO_MODE].append(d)
        elif mode == REPLACED_TEXT_MODE:
            raise ValueError(
                f"Support for {REPLACED_TEXT_MODE} mode is not implemented yet!"
            )
        else:
            raise ValueError(f"Mode {mode} not supported!")

        return result
