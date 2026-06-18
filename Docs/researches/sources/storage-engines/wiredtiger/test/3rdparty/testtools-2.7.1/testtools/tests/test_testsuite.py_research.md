<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py

## Purpose

This module tests `ConcurrentTestSuite`, `ConcurrentStreamTestSuite`, `FixtureSuite`, and `sorted_tests`. It verifies parallel-suite glue, stream event routing, setup-class skip compatibility, fixture wrapping, and deterministic sorting with duplicate-id detection.

## Important APIs, Types, And Functions

- `Sample` is a simple `TestCase` with two methods and identity hashing for suite tests.
- `TestConcurrentTestSuiteRun` checks broken runners, trivial execution, and the `wrap_result` hook for per-thread results.
- `TestConcurrentStreamTestSuiteRun` checks stream-based concurrent execution, broken runner traceback streaming, and class-level `setUpClass` skip/upcall behavior through normal `unittest.TestSuite`.
- `TestFixtureSuite` uses optional `fixtures.FunctionFixture` to assert setup/test/teardown ordering and duplicate sorting failure.
- `TestSortedTests` validates custom suite sorting, custom suites without `sort_tests`, simple sorting, duplicate detection, and multi-duplicate error messages.
- `test_suite()` exposes standard `TestLoader` discovery.

## Control Flow

Concurrent suite tests wrap a standard `unittest.TestSuite`, split it with `iterate_tests`, and run it against either `LoggingResult`, `TestByTestResult`, or `LoggingStream`. Broken runner tests intentionally define objects with invalid `run` signatures so suite code must synthesize a failed "broken-runner" event. Fixture tests run two sample test methods inside a fixture and assert fixture setup before tests and teardown after them.

## State And Persistence Behavior

The file has no persistent state. Test state is stored in local `log`, `wrap_log`, `result_log`, and stream `_events` lists. Optional fixture setup mutates the in-memory log only. Sorting mutates suite internals in custom subclasses when `sort_tests` is called.

## Dependencies

It depends on `doctest`, `pprint.pformat`, `unittest`, testtools suite/result APIs, matchers, `try_import`, and optional `fixtures.FunctionFixture`. It also uses `LoggingResult` from local test helpers and `StreamResult` doubles.

## Integration Points

The suite connects testtools suite implementations with result doubles, stream results, fixture integration, and standard `unittest` class-level setup semantics. It is an important guard for concurrent runners and users relying on deterministic test ordering.

## Risks And Edge Cases

Risks covered include invalid test runner objects, loss of traceback attachments in stream mode, route-code omission in concurrent stream output, wrapper hooks receiving the wrong result/thread number, duplicate ids silently sorting, and fixture teardown not running after all tests.

## Test Signals

Primary signals are exact event tuples, route codes, traceback doctest fragments, setup-class skip event names, fixture log order, sorted `iterate_tests` output, and duplicate-id error text.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testsuite.py -->
