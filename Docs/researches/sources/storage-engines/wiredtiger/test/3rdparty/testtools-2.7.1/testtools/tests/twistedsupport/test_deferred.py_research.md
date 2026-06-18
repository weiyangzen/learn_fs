<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py

## Purpose

This module tests `testtools.twistedsupport._deferred.extract_result` and `DeferredNotFired`, the small helper that synchronously inspects an already-fired Twisted `Deferred`.

## Important APIs, Types, And Functions

- `DeferredNotFired` and `extract_result` are imported with `try_import`.
- `defer` and `Failure` are optional Twisted imports.
- `TestExtractResult` inherits from `NeedsTwistedTestCase`.
- `test_not_fired` expects `extract_result(defer.Deferred())` to raise `DeferredNotFired`.
- `test_success` expects a succeeded deferred to return its callback value.
- `test_failure` expects a failed deferred to re-raise the underlying exception.
- `test_suite()` exposes standard loader integration.

## Control Flow

The tests build three deferred states: pending, succeeded, and failed. `extract_result` is called directly and the result or raised exception is matched through testtools matchers.

## State And Persistence Behavior

No persistent state exists. Deferred objects are local to tests. The failure case captures a `Failure` from the current exception and wraps it with `defer.fail`.

## Dependencies

Depends on `try_import`, matchers `Equals`, `MatchesException`, and `Raises`, `NeedsTwistedTestCase`, and optional Twisted `defer` and `Failure`.

## Integration Points

`extract_result` is a support primitive for Twisted deferred matchers and synchronous/asynchronous runner code that needs to inspect deferred completion without spinning the reactor.

## Risks And Edge Cases

Risks include treating pending deferreds as successful, returning `Failure` objects instead of raising their exceptions, or losing the original failure type.

## Test Signals

Signals are exact exception type for pending/failing deferreds and object identity/equality for successful results.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/twistedsupport/test_deferred.py -->
