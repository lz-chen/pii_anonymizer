from typing import List
from presidio_analyzer import EntityRecognizer, RecognizerResult
from presidio_analyzer.nlp_engine import NlpArtifacts
import datetime


class NorwegianIDRecognizer(EntityRecognizer):
    expected_confidence_level = 0.95

    def load(self) -> None:
        """No loading is required."""
        pass

    def analyze(
            self, text: str, entities: List[str], nlp_artifacts: NlpArtifacts
    ) -> List[RecognizerResult]:
        """
        Analyzes test to find tokens which represent a valid Norwegian ID number
        """
        results = []

        for token in nlp_artifacts.tokens:
            if token.is_digit and self._is_valid(token.text):
                result = RecognizerResult(
                    entity_type="NORWEGIAN_ID",
                    start=token.idx,
                    end=token.idx + len(token),
                    score=self.expected_confidence_level,
                )
                results.append(result)
        return results

    def _is_valid(self, tok):
        # check first
        if len(tok) != 11:
            return False
        day = int(tok[:2])
        month = int(tok[2:4])
        year = int(tok[4:6])
        try:
            datetime.datetime(year=year, month=month, day=day)
        except ValueError as e:
            print(e)
            return False

        return True
