# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_results.py

## Purpose

This file tests result decorators and reporting adapters in `subunit.test_results`. These helpers sit between raw unittest/testtools events and subunit output formats, adding hooks, timestamps, tag/time collapsing, per-test callback aggregation, and CSV reporting. The suite validates event ordering and data preservation rather than wire-format bytes.

## Important APIs, Types, and Test Fixtures

- `LoggingDecorator` subclasses `HookedTestResultDecorator` and increments `_calls` in `_before_event`.
- `AssertBeforeTestResult` asserts that an earlier decorator ran before forwarding reaches this decorator, proving hook order through a decorator chain.
- `TimeCapturingResult` is a minimal `unittest.TestResult` with a `time()` method and `failfast` state used by auto-timing tests.
- `TestHookedTestResultDecorator` exercises forwarding and hook invocation for run lifecycle, test lifecycle, all major outcomes, progress, `wasSuccessful`, `shouldStop`, `stop`, and `time`.
- `TestAutoTimingTestResultDecorator` verifies automatic time emission on real result events, suppression for progress and `shouldStop`, explicit `time()` behavior, `time(None)` re-enabling auto timing, and failfast property propagation.
- `TestTagCollapsingDecorator` verifies that adjacent tag events are collapsed outside and inside tests and flushed before outcome events where ordering matters.
- `TestTimeCollapsingDecorator` verifies that repeated adjacent time events collapse to first and last distinct timestamps before a non-time event.
- `TestByTestResultTests` validates `TestByTestResult`, which converts start/outcome/stop event sequences into one callback per completed test.
- `TestCsvResult` validates CSV output headers and one-row-per-test reporting.

## Control Flow and State Behavior

The decorator tests build chains of result objects and then call result methods through the outer decorator. `HookedTestResultDecorator` is expected to run `_before_event` before forwarding to the decorated result for every observable event-like operation. The ordering fixture proves the outer hook increments its counter before the inner assertion hook runs.

`AutoTimingTestResultDecorator` keeps state about whether explicit time events have been observed. If no explicit time has been sent, it emits a current timestamp before test events. `progress` and `shouldStop` do not trigger automatic timestamps. Calling `time(a_datetime)` forwards that timestamp and suppresses automatic timestamps until `time(None)` is called, which passes `None` through and then allows automatic timing again.

`TagCollapsingDecorator` accumulates pending tag additions/removals. Outside tests, repeated tag events collapse and flush at the next test start or run end. Inside a test, repeated tag updates collapse and flush before the outcome event, preserving protocol semantics where tag placement relative to outcomes matters. Add/remove conflicts are resolved so the final event represents net tag state.

`TimeCollapsingDecorator` buffers consecutive time events. The first time is always forwarded; if multiple distinct times occur before another event, the last distinct time is forwarded just before that next event. Duplicate times collapse to one event. The decorator does not synthesize new times for ordinary test events.

`TestByTestResult` tracks per-test start time, stop time, tags, details, and status. On `stopTest`, it calls the user callback with one dictionary. Exceptions passed as `exc_info` are converted to `TracebackContent`; detail dictionaries are preserved. Unexpected success maps to `status='success'` with supplied details, and skip reason strings are wrapped as text content. `CsvResult` builds on this style to write a header at `startTestRun` and rows for completed tests.

State is in-memory except for CSV writes to a provided text stream. Tests override `_now` with deterministic iterators to make start/stop times predictable.

## Dependencies and Integration Points

The file depends on `csv`, `datetime`, `sys`, `unittest`, `StringIO`, `testtools`, `testtools.content.TracebackContent`, `text_content`, and `ExtendedTestResult`. It imports `subunit`, `iso8601`, and `subunit.test_results`. These decorators integrate with both stdlib `unittest.TestResult` and testtools extended APIs, so they are important adapters between raw result event producers and subunit stream writers.

## Risks and Maintenance Signals

- Decorator forwarding must preserve subtle property behavior such as `failfast` and `shouldStop`, not just method calls.
- Tag ordering is protocol-sensitive; tags must be emitted before outcomes when they apply to a test.
- Automatic time insertion can create noisy or misleading streams if it triggers on non-event probes such as `shouldStop`; the tests guard against this.
- `TestByTestResult` assumes a well-formed start/outcome/stop lifecycle. Out-of-order or missing events are not deeply tested here.
- CSV tests validate minimal output only; quoting, newline handling, and unusual test IDs depend on Python's `csv` module but are not exhaustively covered.

## Test Signals

The suite provides strong event-order assertions using `ExtendedTestResult._events`, deterministic timing via `_now`, callback payload equality for each outcome, and CSV reader checks for output shape. It is the main local signal for changes to `subunit.test_results` decorators and summary/reporting adapters.
