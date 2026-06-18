<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py

## Purpose

This module tests the `ExpectedException` context manager exported by testtools. It validates exception-type matching, optional message regex matching, matcher-based validation, custom annotation text, and correct pass-through of unexpected exceptions.

## Important APIs, Types, And Functions

- `TestExpectedException` is the single test class.
- `test_pass_on_raise` and `test_pass_on_raise_matcher` prove the context manager suppresses matching exceptions.
- Mismatch tests prove regex mismatches and matcher mismatches become `AssertionError` with useful messages.
- `test_raise_on_error_mismatch` proves unexpected exception types are re-raised rather than converted.
- `test_raise_if_no_exception` proves missing exceptions fail with "`TypeError not raised.`".
- Annotation tests verify `msg` is appended to failure messages.
- `test_suite()` exposes standard loader integration.

## Control Flow

Each test enters `with ExpectedException(...)`; the context manager observes the exception exiting the block. If the type and optional message/matcher match, execution proceeds. If no exception or the wrong message occurs, the test catches `AssertionError` and compares its text. If a different exception type occurs, the original exception is expected outside the context.

## State And Persistence Behavior

No persistent state exists. Temporary local exception objects and matcher instances are created only for the assertion under test.

## Dependencies

The module uses `sys.exc_info`, `ExpectedException`, `TestCase`, and matchers `AfterPreprocessing`, `Equals`, and `EndsWith`.

## Integration Points

This tests the context-manager API used by external test authors who prefer `with` blocks to `assertRaises` calls. It also validates matcher integration for exception values.

## Risks And Edge Cases

Risks include swallowing unexpected exceptions, producing misleading messages for regex or matcher mismatches, failing to report missing exceptions, and losing caller-supplied annotation text.

## Test Signals

Signals are successful context exit for matched exceptions and exact `AssertionError` text for mismatch/no-exception cases.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_with_with.py -->
