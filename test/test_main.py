#!/usr/bin/env python3

""" Main test module for the Spectra steno lexer. Currently handles all major components except the GUI. """

from collections import Counter
import os
import re

import pytest

from spectra_lexer import plover
from spectra_lexer.app import StenoMain
from spectra_lexer.io import ResourceIO
from spectra_lexer.steno import RuleFlags
from spectra_lexer.steno.search import IndexSearchDict, TranslationsSearchDict


def _test_file_path(filename:str) -> str:
    """ Get the full file path for program test data by type (e.g. translations that should all pass with matches). """
    return os.path.join(__file__, "..", "data", filename)


# Load resources using default command-line arguments and create components as we need them.
opts = StenoMain()
IO = ResourceIO()
RESOURCES = opts.build_resources()
STENO = RESOURCES.build_engine()
RULES_DICT = STENO._rule_parser.to_dict()
IGNORED_KEYS = set("/-")
VALID_FLAGS = {v for v in vars(RuleFlags).values() if isinstance(v, str)}


@pytest.mark.parametrize("rule", RULES_DICT.values())
def test_rules(rule) -> None:
    """ Go through each rule and perform integrity checks. First verify that all flags are valid. """
    flags = rule.flags
    for f in flags:
        assert f in VALID_FLAGS, f"Entry {rule} has illegal flag: {f}"
    rulemap = rule.rulemap
    if rulemap:
        # Check that the rulemap positions all fall within the legal bounds (i.e. within the parent's letters)
        # Make sure the child rules contain all the keys of the parent between them, and no extras.
        parent_len = len(rule.letters)
        key_count = Counter(rule.keys)
        for item in rulemap:
            assert item.start >= 0
            assert item.length >= 0
            assert item.start + item.length <= parent_len
            key_count.subtract(item.rule.keys)
        mismatched = [k for k in key_count if key_count[k] and k not in IGNORED_KEYS]
        assert not mismatched, f"Entry {rule} has mismatched keys vs. its child rules: {mismatched}"


TRANSLATIONS = [*IO.json_read(_test_file_path("translations.json")).items()]
TRANSLATIONS_DICT = TranslationsSearchDict(TRANSLATIONS)


@pytest.mark.parametrize("keys, word", TRANSLATIONS)
def test_translations_search(keys, word) -> None:
    """ Go through each loaded test translation and check the search method in all modes.
        Search should return a list with only the item itself (or its value) in any mode. """
    assert TRANSLATIONS_DICT.search(keys, count=2, strokes=True) == [keys]
    assert TRANSLATIONS_DICT.search(word, count=2, strokes=False) == [word]
    assert TRANSLATIONS_DICT.search(keys, count=None, strokes=True) == [word]
    assert TRANSLATIONS_DICT.search(word, count=None, strokes=False) == [keys]
    assert TRANSLATIONS_DICT.search(re.escape(keys), count=2, strokes=True, regex=True) == [keys]
    assert TRANSLATIONS_DICT.search(re.escape(word), count=2, strokes=False, regex=True) == [word]


INDEX = [*IO.json_read(_test_file_path("index.json")).items()]
INDEX_DICT = IndexSearchDict(INDEX)


@pytest.mark.parametrize("rule_name", INDEX_DICT.keys())
def test_index_search(rule_name) -> None:
    """ Any rule with translations in the index should have its keys and letters somewhere in every entry. """
    rule = RULES_DICT[rule_name]
    wresults = INDEX_DICT.search(rule_name, "", count=100, strokes=False)
    assert all([rule.letters in r for r in wresults])
    kresults = INDEX_DICT.search(rule_name, "", count=100, strokes=True)
    all_keys = set(rule.keys) - IGNORED_KEYS
    assert all_keys == all_keys.intersection(*kresults)


RESULTS = [STENO.lexer_query(*t, match_all_keys=True) for t in TRANSLATIONS]


@pytest.mark.parametrize("result", RESULTS)
def test_lexer(result) -> None:
    """ The parsing tests fail if the parser can't match all the keys. """
    rulemap = result.rulemap
    assert rulemap, f"Lexer failed to match all keys on {result.keys} -> {result.letters}."


@pytest.mark.parametrize("result", RESULTS)
def test_board(result) -> None:
    """ Perform all tests for board diagram output. Currently only checks that the output doesn't raise. """
    STENO.board_from_keys(result.keys)
    STENO.board_from_rule(result)


@pytest.mark.parametrize("result", RESULTS)
def test_graph(result) -> None:
    """ Perform all tests for text graph output. Mainly limited to examining the node tree for consistency. """
    graph = STENO.graph_generate(result)
    tree = graph._tree
    # The root node uses the top-level rule and has no parent.
    indexed_nodes = list(tree._rules)
    root = indexed_nodes[0]
    assert tree.get_ancestors(root) == [root]
    # Every node available for interaction descends from it and is unique.
    # (FUN FACT: if you iterate over a tree with a self-modifying list, people will hate you).
    nodes_list = [root]
    for node in nodes_list:
        nodes_list += tree._children.get(node) or ()
    nodes_set = set(nodes_list)
    assert len(nodes_list) == len(nodes_set)
    assert nodes_set >= set(indexed_nodes)


def test_plover() -> None:
    """ Make sure the Plover plugin can convert dicts between tuple-based keys and string-based keys. """
    plover.test_convert(TRANSLATIONS_DICT)
