# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/matchers/test_datastructures.py

## Purpose
This module tests matchers for structured objects and collections: listwise matching, attribute-structure matching, setwise matching, and contains-all composition.

## Important APIs, types, and functions
It imports `MatchesListwise`, `MatchesStructure`, `MatchesSetwise`, and `ContainsAll` from `_datastructures`. `run_doctest()` runs doctests from matcher docstrings. `TestMatchesStructure` exercises `fromExample`, `byEquality`, `byMatcher`, and `update`. `TestMatchesSetwise` checks exact matches and detailed diagnostics for mismatches, extra matchers, extra values, and combined cases.

## Control flow
`TestMatchesListwise` executes the `MatchesListwise` docstring through `doctest`. Interface-based tests use example tables. Setwise tests call `matcher.match(value)`, fail if it unexpectedly matches, then compare the description against exact strings or regexes.

## State and persistence behavior
There is no persistent state. Temporary structures are in-memory objects, lists, tuples, iterators, and simple classes with attributes.

## Dependencies and integration points
The module depends on `doctest`, `io`, `re`, `sys`, base matchers, and shared matcher helpers. It verifies matcher APIs used heavily by testtools assertions and by other test helpers such as `MatchesEvents`.

## Risks and test signals
Setwise diagnostics rely on formatting and ordering of leftover matchers/values, so regexes are used where order may vary. `MatchesStructure.update(z=None)` encodes the convention that `None` removes a field matcher. The doctest path signals documentation drift.
