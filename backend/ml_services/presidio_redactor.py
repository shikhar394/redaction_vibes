import logging
import sys
from typing import Dict

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from llama_index.core.postprocessor import (
    PIINodePostprocessor,
    NERPIINodePostprocessor,
)
from llama_index.llms.huggingface import HuggingFaceLLM
from llama_index.core import Document, VectorStoreIndex
from llama_index.core.schema import TextNode
from llama_index.postprocessor.presidio import PresidioPIINodePostprocessor
from llama_index.core.schema import NodeWithScore
from pprint import pprint 
from presidio_analyzer import AnalyzerEngine
import re

class TextRedactor():
    def __init__(self) -> None:
        pass

    def redact(self) -> str:
        raise NotImplementedError("Subclasses should implement this method")
    
    def stitch(self) -> str:
        raise NotImplementedError("Subclasses should implement this method")

    
class PresidioTextRedactor(TextRedactor):
    def __init__(self, text: str):
        super().__init__()
        self.processor = PresidioPIINodePostprocessor()
        self.text = text

    def redact(self) -> Dict:
        presidio_node = TextNode(text=self.text)
        presidio_new_nodes = self.processor.postprocess_nodes(
            [NodeWithScore(node=presidio_node)]
        )
        self.redacted_tokens = presidio_new_nodes[0].node.metadata["__pii_node_info__"]

        entities=["US_SSN", "CREDIT_CARD", "IBAN_CODE",
                "US_BANK_NUMBER", "US_DRIVER_LICENSE",
                "US_ITIN", "US_PASSPORT", "LOCATION"
        ]

        redacted_tokens = {}

        for token in self.redacted_tokens:
            for entity in entities:
                if entity in token:
                    redacted_tokens[token] = self.redacted_tokens[token]
                    break

        self.redacted_tokens = redacted_tokens

        redacted_text = self.text

        for redact_token, original_value in self.redacted_tokens.items():
            redacted_text = redacted_text.replace(
                    original_value, redact_token
            )

        pprint(self.redacted_tokens)

        return redacted_text
    
    
    def stitch(self) -> str:
        if self.redacted_text is None:
            raise ValueError("Redacted text is not available. Run redact() first.")
        
        return self.redacted_text
    
class FintechTextRedactor(TextRedactor):
    def __init__(self, text: str):
        super().__init__()
        self.analyzer = AnalyzerEngine()
        self.text = text
        self.all_components = []

    def redact(self) -> Dict:
        component_count = {}
        results = self.analyzer.analyze(text=text,
                           entities=["US_SSN", "CREDIT_CARD", "IBAN_CODE",
                                     "US_BANK_NUMBER", "US_DRIVER_LICENSE",
                                     "US_ITIN", "US_PASSPORT", "LOCATION"],
                           language='en')
        
        for result in results:
            component = re.findall(r'type: (\w+), start: (\d+), end: (\d+), score: ([\d.]+)', str(result))[0]

            if component[0] in component_count:
                component_count[component[0]] += 1
            else:
                component_count[component[0]] = 1

            self.all_components.append(
                {
                    "type": component[0] + "_" + str(component_count[component[0]]), "start": int(component[1]), "end": int(component[2])
                }
            )

        annotations = sorted(self.all_components, key=lambda x: x['start'], reverse=True)
        pprint(annotations)

        # Replace each segment in the text with the corresponding type
        for annotation in annotations:
            self.text = self.text[:annotation['start']] + "<" + annotation['type'] + ">" + self.text[annotation['end']:]

        print(self.text)


    def store_pii(self, pii):
        pass

    def stitch(self) -> str:
        if self.redacted_text is None:
            raise ValueError("Redacted text is not available. Run redact() first.")
        
        for redact_token, original_value in self.redacted_tokens.items():
            self.redacted_text = self.redacted_text.replace(
                    redact_token, original_value
            )
        return self.redacted_text
    

if __name__ == "__main__":
    text = """
        My name is Roey Ben Chaim and my credit card number is 4095-2609-9393-4932. 
        My email is robo@presidio.site and I live in Amsterdam.
        What is the limit for card 4158112277712? My IBAN is GB90YNTU67299444055881. 
        What's your last name? Bob, it's Bob.
        Can you share your SSN? SSN: 123467891
        I can't browse to your site, keep getting address 179.177.214.91 blocked error
        Just posted a photo https://www.FilmFranchise.dk/
    """
    # analyzer = AnalyzerEngine()
    # results = analyzer.analyze(text=text,
    #                        entities=["US_SSN", "CREDIT_CARD"],
    #                        language='en')
    # print(results)
    # redactor = PresidioTextRedactor(text)
    # redacted_text = redactor.redact()
    # stitched_text = redactor.stitch()

    # print(redacted_text)

    # print(stitched_text)
    redactor = PresidioTextRedactor(text)
    print(redactor.redact())