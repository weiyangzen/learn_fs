# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_basic.py

Purpose: primitive matchers for equality, identity, ordering, membership, type checks, string prefixes/suffixes, regexes, length, and multiset-like member comparison.

Important APIs, types, and functions: `Equals`, `NotEquals`, `Is`, `LessThan`, and `GreaterThan` derive from `_BinaryComparison`. `_BinaryMismatch` formats compact or multi-line differences. `SameMembers`, `StartsWith`, `EndsWith`, `IsInstance`, `Contains`, `MatchesRegex`, and `HasLength` provide common assertions. `_FlippedEquals` supports `TestCase.assertEqual` expected/observed ordering.

Control flow: matchers return `None` on success or a `Mismatch` object on failure. `SameMembers` subtracts observed and expected lists while preserving duplicates. `MatchesRegex` uses `re.match`, not search, and formats escaped patterns.

State and persistence: matcher instances store expected values; mismatch instances store actual/reference values. No external state.

Dependencies and integration points: depends on `operator`, `pprint`, `re`, `warnings`, `text_repr`, list helpers, higher-order predicate factory, and core matcher classes. Used by most other matchers and `TestCase` assertions.

Risks and test signals: `FileContains.__str__` elsewhere expects a `contents` attribute not set by this module, but `_basic` itself is straightforward. Regex users may expect substring matching but receive start-anchored `re.match`. Tests cover mismatch text, duplicate handling, deprecation warnings, and length predicate behavior.
