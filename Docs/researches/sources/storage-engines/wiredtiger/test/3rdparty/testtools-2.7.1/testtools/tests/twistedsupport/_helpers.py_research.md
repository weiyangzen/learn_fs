<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py

## Purpose

This helper module provides a Twisted-aware base test class for the Twisted support test suite. It centralizes optional dependency skipping.

## Important APIs, Types, And Functions

- `__all__ = ['NeedsTwistedTestCase']` declares the exported helper.
- `defer = try_import('twisted.internet.defer')` records whether Twisted is importable.
- `NeedsTwistedTestCase(TestCase)` overrides `setUp`; after calling `super().setUp()`, it calls `skipTest("Need Twisted to run")` when Twisted is unavailable.

## Control Flow

Each Twisted test class inherits from `NeedsTwistedTestCase`. During setup, tests are skipped before Twisted-specific behavior runs if `try_import` failed.

## State And Persistence Behavior

State is module-level and immutable after import for normal use: `defer` is either the Twisted defer module or `None`. There is no persistent state.

## Dependencies

Depends on `testtools.helpers.try_import` and `testtools.TestCase`. Optionally depends on `twisted.internet.defer`.

## Integration Points

This helper gates all Twisted support tests in the same way, allowing the broader testtools test suite to run in environments where Twisted is not installed.

## Risks And Edge Cases

If Twisted is partially installed such that `defer` imports but later Twisted modules fail, this helper will not skip those later failures. It only validates the base `twisted.internet.defer` import.

## Test Signals

The signal is skip behavior at setup time when `defer is None`; otherwise subclasses proceed normally.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/_helpers.py -->
