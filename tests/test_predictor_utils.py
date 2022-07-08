import unittest

import spacy

from container.anonymizer.utils import detect_lang


class TestPredictorUtils(unittest.TestCase):

    def setUp(self) -> None:
        self.nlp = spacy.load("en_core_web_sm", disable=["tagger", "ner"])
        self.nlp.add_pipe('language_detector', last=True)

    def test_lang_detect_en(self):
        text = "This is a English text"
        lang = detect_lang(text, self.nlp)
        self.assertEqual(lang, 'en')

    def test_lang_detect_no(self):
        text = "Dette er en norsk tekst"
        lang = detect_lang(text, self.nlp)
        self.assertEqual(lang, 'no')
