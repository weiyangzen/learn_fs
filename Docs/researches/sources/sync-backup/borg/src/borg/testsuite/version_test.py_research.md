# sources/sync-backup/borg/src/borg/testsuite/version_test.py

## Purpose
Tests Borg's remote-protocol version tuple parser and formatter. It ensures setuptools-scm-derived strings collapse into stable comparable tuples and that tuple formatting reverses the supported subset.

## Important APIs, Types, and Functions
Exercises `parse_version` and `format_version` from `borg.version` with pytest parametrization. Supported prerelease tags are `.dev`, `a`, `b`, and `rc`; final releases use sentinel `-1`.

## Control Flow
Parameterized parse tests pass final versions, prereleases, and setuptools local/date suffix examples. Invalid strings lacking `x.y.z` shape are expected to raise `ValueError`. Format tests convert tuples back to canonical strings.

## State and Persistence Behavior
No mutable state. The tuple format is effectively protocol state because remote compatibility depends on stable ordering semantics.

## Dependencies and Integration Points
This file directly guards `borg.version`, which is consumed by remote negotiation and version comparisons.

## Risks and Test Signals
Risks are changing tuple encodings in a remote-protocol-breaking way, accepting malformed short versions, or formatting prereleases incorrectly. Signals are exact tuple equality and exact string equality.
