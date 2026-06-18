# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/matchers/_datastructures.py

Purpose: matchers for lists, sets, object attributes, and containment across Python data structures.

Important APIs, types, and functions: `ContainsAll(items)` builds a `MatchesAll` of `Contains` matchers. `MatchesListwise` matches values positionally and checks length. `MatchesStructure` matches named attributes using supplied matchers, with constructors `byEquality`, `byMatcher`, and `fromExample`, plus `update()`. `MatchesSetwise` matches observed values to matchers without regard to order, requiring one-to-one matching.

Control flow: listwise matching first annotates length mismatch, then zips matchers and values. Structure matching extracts attributes in sorted key order and delegates to `MatchesListwise`. Setwise matching greedily removes the first remaining matcher that matches each observed value, then builds diagnostic messages for leftover values/matchers.

State and persistence: matcher instances hold matcher lists/dicts. No persistent state.

Dependencies and integration points: depends on helper `map_values`, higher-order matchers, and core `Mismatch`. Used by warning and dict matchers and by test suites asserting structured events.

Risks and test signals: `MatchesSetwise` uses a greedy algorithm, so ambiguous matcher/value combinations may produce non-optimal diagnostics. Structure matching raises `AttributeError` if an expected attribute is absent. Test signals cover length mismatch, first-only reporting, structural updates, and leftover setwise diagnostics.
