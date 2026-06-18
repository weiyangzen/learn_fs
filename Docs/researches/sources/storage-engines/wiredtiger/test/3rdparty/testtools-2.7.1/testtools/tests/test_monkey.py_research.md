# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_monkey.py

## Purpose
This module tests `testtools.monkey` monkey-patching utilities.

## Important APIs, types, and functions
`TestObj` is a simple object with `foo`, `bar`, and `baz` attributes. `MonkeyPatcherTest` covers `MonkeyPatcher` construction, adding patches, patching existing and missing attributes, restoring, overriding repeated patches, idempotent restore, and `run_with_patches()`. `TestPatchHelper` covers the convenience `patch()` function and its returned cleanup.

## Control flow
Each test creates a fresh `TestObj` and `MonkeyPatcher`. Patches are added, applied, observed, and restored. `run_with_patches()` is tested for argument forwarding, return value preservation, repeated use, restoration after success, and restoration after exceptions.

## State and persistence behavior
The module mutates object attributes in memory and restores them. It verifies that missing attributes are deleted on restore and that double restore is a no-op.

## Dependencies and integration points
It depends on `MonkeyPatcher`, `patch`, exception matchers, and `TestCase`. Monkey-patching is used in other tests for controlled environment changes.

## Risks and test signals
The core risk is leaking patched state after exceptions. Tests explicitly cover exception safety and idempotent cleanup, making this file a strong signal for state isolation.
