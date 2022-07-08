from spacy.language import Language
from spacy_langdetect import LanguageDetector


@Language.factory('language_detector')
def get_lang_detector(nlp, name):
    return LanguageDetector()


def detect_lang(text, nlp):
    return nlp(text)._.language["language"]
