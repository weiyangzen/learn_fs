# sources/security-integrity/selinux/python/sepolgen/tests/test_matching.py

## Purpose
This file tests the ranking containers used to match access vectors against reference-policy interfaces. It also contains a minimal smoke path for `AccessMatcher.search_ifs()`.

## Important Tests And Exercised APIs
`TestMatch` validates `matching.Match` equality and ordering by distance and information-flow direction-change flags. `TestMatchList` validates threshold handling, the `bastards` collection for weak/disallowed matches, sorting, and `best()`.

`AccessMatcher.test_search()` parses embedded interface text, builds an `InterfaceSet`, creates an access vector, and invokes `matching.AccessMatcher().search_ifs(...)` with a `MatchList`, but it has no assertions after the call.

## Control Flow
The ranking tests construct `Match` objects manually and append them to `MatchList`. The access matcher smoke test follows the same parser and interface expansion path as `test_interfaces.py`, then exercises matching search code.

## State And Persistence
All state is in memory: `Match.dist`, `Match.info_dir_change`, `MatchList.threshold`, `allow_info_dir_change`, and `bastards`.

## Dependencies And Integration Points
It imports `sepolgen.matching`, `sepolgen.refparser`, `sepolgen.interfaces`, and `sepolgen.access`. The smoke test integrates parser output, interface expansion, access vectors, and matching search.

## Risks And Edge Cases
The most important integration call has no assertions, so regressions in match quality or result contents could pass as long as no exception is raised. The name `bastards` is an internal compatibility detail that tests couple to directly. Threshold and direction-change logic are covered only with a few scalar examples.

## Test Signals
Useful signals exist for ordering and threshold bucketing. Search behavior is only a smoke signal and should not be treated as comprehensive matching validation.
