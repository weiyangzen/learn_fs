# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_dict.py

Purpose: dictionary-specific matchers for exact dict matches, contains/subset relations, contained-by/superset relations, common-key value matching, and key equality.

Important APIs, types, and functions: `MatchesAllDict` labels mismatches by dictionary key. `DictMismatches` formats nested mismatch dictionaries. `_MatchCommonKeys`, `_SubDictOf`, and `_SuperDictOf` implement common-key, extra-key, and missing-key checks. `MatchesDict`, `ContainsDict`, and `ContainedByDict` combine these primitives. `KeysEqual` compares sorted keys.

Control flow: combined matchers build a dict of named matcher factories from expected data, run each against the observed dict, filter successful entries, and return labelled mismatch groups. `KeysEqual` special-cases a single mapping argument by using its keys.

State and persistence: matcher instances store expected dictionaries or key lists. No persistence.

Dependencies and integration points: depends on helper functions and higher-order mismatch decorators. Used by testtools tests and downstream code asserting structured dictionaries.

Risks and test signals: sorted keys require comparable key types; mixed incomparable keys can fail in Python 3. Value comparison only occurs on common keys, with missing/extra keys reported separately. Tests should cover exact, contains, contained-by, and key-only diagnostics.
