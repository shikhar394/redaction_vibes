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
        self.redacted_text = presidio_new_nodes[0].node.get_text()
        
        return {
            'redacted_text': self.redacted_text,
            'redacted_tokens': self.redacted_tokens
        }
    
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
        Have you been to a Pálmi Einarsson concert before?
        What is the limit for card 4158112277712? My IBAN is GB90YNTU67299444055881. 
        What's your last name? Bob, it's Bob.
        My great great grandfather was called Yulan Peres, 
        and my great great grandmother was called Jennifer Holst
        I can't browse to your site, keep getting address 179.177.214.91 blocked error
        Just posted a photo https://www.FilmFranchise.dk/
    """
    redactor = PresidioTextRedactor(text)
    redacted_text = redactor.redact()
    stitched_text = redactor.stitch()

    print(redacted_text)

    print(stitched_text)
