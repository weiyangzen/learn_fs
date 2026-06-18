# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_tags.py

## Purpose
This module tests `TagContext`, the data structure used to maintain current test tags across nested scopes.

## Important APIs, types, and functions
`TestTags` covers empty contexts, adding tags, adding multiple tags, return value from `change_tags`, removing tags, child contexts, child-only additions/removals, and the `parent` attribute.

## Control flow
Each test constructs `TagContext`, calls `change_tags(new_tags, gone_tags)`, and compares `get_current_tags()` against expected sets. Child tests create a parent with tags, instantiate a child from it, mutate the child, and verify the parent is unaffected.

## State and persistence behavior
State is in-memory tag sets. Child contexts copy effective parent tags at construction while preserving a parent reference.

## Dependencies and integration points
It depends on `testtools.tags.TagContext` and `TestCase`. `TagContext` is used by `TestResult`, result adapters, and thread-safe forwarding for scoped tags.

## Risks and test signals
The main risks are accidental parent mutation, incorrect remove semantics, and losing the convenience return value from `change_tags`. These tests provide direct coverage for tag scoping used throughout result handling.
