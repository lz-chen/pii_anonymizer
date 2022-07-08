import unittest
from container.anonymizer.constants import SUPPORTED_LANG, TAGGED_TEXT_MODE, DETAIL_INFO_MODE, REPLACED_TEXT_MODE
from container.anonymizer.pii_anonymizer import PiiAnonymizer
from ddt import ddt, data, unpack

TEXT_EN = "Hello this is Jamie Clark calling, my phone number is 212-555-5555"
TEXT_EN_ANNO = "Hello this is <PERSON> calling, my phone number is <PHONE_NUMBER>"
TEXT_EN_INFO = [{'end': 25,
                 'entity': 'Jamie Clark',
                 'entity_type': 'PERSON',
                 'start': 14},
                {'end': 66,
                 'entity': '212-555-5555',
                 'entity_type': 'PHONE_NUMBER',
                 'start': 54}]

TEXT_NO = "Andreas Hansen, IT Sjef Bla Bla E-post: ahansen@blabla.com Tlf. 98 45 76 29"
TEXT_NO_ANNO = "<PERSON>, IT Sjef Bla Bla E-post: <EMAIL_ADDRESS> Tlf. <PHONE_NUMBER>"
TEXT_NO_INFO = [{'end': 58,
                 'entity': 'ahansen@blabla.com',
                 'entity_type': 'EMAIL_ADDRESS',
                 'start': 40},
                {'end': 14,
                 'entity': 'Andreas Hansen',
                 'entity_type': 'PERSON',
                 'start': 0},
                {'end': 58,
                 'entity': 'blabla.com',
                 'entity_type': 'URL',
                 'start': 48},
                {'end': 75,
                 'entity': '98 45 76 29',
                 'entity_type': 'PHONE_NUMBER',
                 'start': 64}]


@ddt
class TestPredictor(unittest.TestCase):

    def setUp(self) -> None:
        self.pii_anonymizer = PiiAnonymizer()

    def test_load_analyzer_engine(self):
        analyzer = PiiAnonymizer._load_analyzer_engine()
        self.assertTrue(set(SUPPORTED_LANG), set(analyzer.supported_languages))

    @data(
        (TEXT_EN, "en", TEXT_EN_ANNO),
        (TEXT_NO, "no", TEXT_NO_ANNO),
    )
    @unpack
    def test_anonymize_text_tag(self, text, lang, expected):
        anonymized_text = self.pii_anonymizer.anonymize_text(text, mode=TAGGED_TEXT_MODE, lang=lang)[TAGGED_TEXT_MODE]
        self.assertEqual(expected, anonymized_text)

    def test_anonymize_text_tag_other_lang(self):
        text = "This is a piece of text"
        lang = "es"
        with self.assertRaises(ValueError) as context:
            anonymized_text = self.pii_anonymizer.anonymize_text(text, mode=TAGGED_TEXT_MODE, lang=lang)[
                TAGGED_TEXT_MODE]

        self.assertEqual("Support for language es is not implemented yet!", context.exception.args[0])

    @data(
        (TEXT_EN, "en", TEXT_EN_INFO),
        (TEXT_NO, "no", TEXT_NO_INFO),
    )
    @unpack
    def test_anonymize_text_detail(self, text, lang, expected):
        check_list = ['end', 'entity', 'entity_type', 'start']
        anonymized_text = self.pii_anonymizer.anonymize_text(text, mode=DETAIL_INFO_MODE, lang=lang)[DETAIL_INFO_MODE]
        for idx, item in enumerate(anonymized_text):
            for key in check_list:
                self.assertEqual(expected[idx][key], item[key])

    def test_anonymize_text_replaced(self):
        text = "This is a piece of text"
        with self.assertRaises(ValueError) as context:
            anonymized_text = self.pii_anonymizer.anonymize_text(text, mode=REPLACED_TEXT_MODE)
        self.assertEqual("Support for replaced_text mode is not implemented yet!", context.exception.args[0])

    def test_anonymize_text_other(self):
        text = "This is a piece of text"
        with self.assertRaises(ValueError) as context:
            anonymized_text = self.pii_anonymizer.anonymize_text(text, mode="random")
        self.assertEqual("Mode random not supported!", context.exception.args[0])
