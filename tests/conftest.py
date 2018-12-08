from typing import Dict, Tuple

import pytest
import spacy
from spacy.language import Language as SpacyModelType
from spacy.cli.download import download as spacy_download

from SciSpaCy.custom_sentence_segmenter import combined_rule_sentence_segmenter
from SciSpaCy.custom_tokenizer import combined_rule_tokenizer, combined_rule_prefixes, remove_new_lines

LOADED_SPACY_MODELS: Dict[Tuple[str, bool, bool, bool], SpacyModelType] = {}


def get_spacy_model(spacy_model_name: str,
                    pos_tags: bool,
                    parse: bool,
                    ner: bool,
                    with_custom_tokenizer: bool = False,
                    with_sentence_segmenter: bool = False) -> SpacyModelType:
    """
    In order to avoid loading spacy models repeatedly,
    we'll save references to them, keyed by the options
    we used to create the spacy model, so any particular
    configuration only gets loaded once.
    """
    options = (spacy_model_name, pos_tags, parse, ner, with_custom_tokenizer, with_sentence_segmenter)
    if options not in LOADED_SPACY_MODELS:
        disable = ['vectors', 'textcat']
        if not pos_tags:
            disable.append('tagger')
        if not parse:
            disable.append('parser')
        if not ner:
            disable.append('ner')
        try:
            spacy_model = spacy.load(spacy_model_name, disable=disable)
        except OSError:
            print(f"Spacy models '{spacy_model_name}' not found.  Downloading and installing.")
            spacy_download(spacy_model_name)
            spacy_model = spacy.load(spacy_model_name, disable=disable)

        if with_custom_tokenizer:
            spacy_model.tokenizer = combined_rule_tokenizer(spacy_model)
        if with_sentence_segmenter:
            spacy_model.add_pipe(combined_rule_sentence_segmenter, first=True)

        LOADED_SPACY_MODELS[options] = spacy_model
    return LOADED_SPACY_MODELS[options]


@pytest.fixture()
def combined_rule_tokenizer_fixture():
    nlp = get_spacy_model('en_core_web_sm', True, True, True)
    tokenizer = combined_rule_tokenizer(nlp)
    return tokenizer

@pytest.fixture()
def en_with_combined_rule_tokenizer_fixture():
    nlp = get_spacy_model('en_core_web_sm', True, True, True, with_custom_tokenizer=True)
    return nlp

@pytest.fixture()
def en_with_combined_rule_tokenizer_and_segmenter_fixture():
    nlp = get_spacy_model('en_core_web_sm', True, True, True,
                          with_custom_tokenizer=True,
                          with_sentence_segmenter=True)
    return nlp

@pytest.fixture()
def combined_rule_prefixes_fixture():
    return combined_rule_prefixes()

@pytest.fixture()
def remove_new_lines_fixture():
    return remove_new_lines

@pytest.fixture()
def default_en_tokenizer_fixture():
    nlp = get_spacy_model('en_core_web_sm', True, True, True)
    return nlp.tokenizer

@pytest.fixture()
def default_en_model_fixture():
    nlp = get_spacy_model('en_core_web_sm', True, True, True)
    return nlp
