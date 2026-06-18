# Research: sources/security-integrity/selinux/python/sepolicy/sepolicy/booleans.py

## Purpose
This small helper supports boolean-related policy exploration by finding target types a source domain may access for a given object class and permission list. It is essentially a thin wrapper around the main `sepolicy` query facade.

## Important APIs and control flow
`expand_attribute(attribute)` calls `sepolicy.info(sepolicy.ATTRIBUTE, attribute)` and returns the first record's `types`; if the lookup raises `RuntimeError`, it treats the input as a concrete type and returns a single-item list. `get_types(src, tclass, perm)` searches allow rules with source, class, and requested permissions, raises `TypeError` if there are no matching allow rules, filters the returned rules to entries whose `permlist` contains all requested permissions, expands each target if it is an attribute, and returns a flat list of target types.

## State and persistence
The file owns no state. It relies entirely on `sepolicy` module-level policy loading and caches. It does not persist data or modify SELinux state.

## Dependencies and integration points
The only dependency is `sepolicy`. The expected integration is from command-line tooling or higher-level analysis that wants to list type targets gated by a boolean or permission relationship.

## Risks and edge cases
The exception handling in `expand_attribute()` differs from the newer generator-return style used in `sepolicy.info()`; if an attribute is absent and the generator raises `StopIteration` instead of `RuntimeError`, the exception can escape. `get_types()` uses permissive list concatenation and does not deduplicate expanded attributes. It assumes every returned rule has a `permlist` key, which may not hold for all rule dictionaries. The error type differs from `communicate.py`, which raises `ValueError` for the same no-allow condition.

## Test signals
Tests should mock `sepolicy.search()` and `sepolicy.info()` for concrete targets, attribute targets, missing attributes, no allow rules, partial permission matches, and duplicate attribute expansion. A compatibility test should capture whether missing attribute lookup raises `RuntimeError` or `StopIteration` under the current `sepolicy.info()` implementation.
