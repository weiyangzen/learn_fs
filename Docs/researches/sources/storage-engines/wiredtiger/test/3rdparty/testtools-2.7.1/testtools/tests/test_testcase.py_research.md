<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py

## Purpose

This module is the main behavioral contract suite for `testtools.testcase` and the testtools extensions exported through `testtools.__init__`. It validates placeholder test objects, error holders, `TestCase` identity/equality, assertion helpers, expectation handling, cleanup execution, expected failures, details propagation, unique-name factories, cloning, lifecycle correctness, skipping decorators, exception hooks, monkey patch cleanup, `Nullary`, attribute-tagged ids, and `DecorateTestCaseResult`.

The file is test code, but it acts as executable API documentation for the compatibility boundary between testtools and `unittest` result implementations.

## Important APIs, Types, And Functions

- `TestPlaceHolder` checks `PlaceHolder` id/description/repr/count/run/debug/call behavior, detail/timestamp emission, tag scoping, and hashability inherited from `unittest.TestCase`.
- `TestErrorHolder` checks the deprecated-but-supported `ErrorHolder`, including id/description/count/run/debug/call behavior and `addError` detail emission.
- `TestEquality` asserts that `TestCase` equality is identity based and handles objects lacking `__dict__`.
- `TestAssertions` covers assertion helpers including `assertRaises`, `assertRaisesRegex`, `assertIn`, `assertNotIn`, `assertIsInstance`, identity assertions, `assertThat`, `expectThat`, `force_failure`, pretty equality formatting, non-ASCII formatting, and preservation of preexisting traceback details.
- `TestAddCleanup` validates cleanup ordering and aggregation: cleanups run after `tearDown`, run even after `setUp` failure, execute in reverse registration order, continue after failures, aggregate multiple traceback details, and re-raise `KeyboardInterrupt`.
- `TestExpectedFailure` covers internal `_UnexpectedSuccess`, `expectFailure`, `unittest.expectedFailure`, and expected-failure details such as `reason` and `traceback`.
- `TestUniqueFactories` covers `getUniqueInteger`, `getUniqueString`, `unique_text_generator`, `_mods`, and `_unique_text`.
- `TestCloneTestWithNewId` verifies cloned tests have rewritten ids but do not share details dictionaries.
- `TestDetailsProvided` checks details for errors, failures, skips, success, unexpected success, mismatch details, duplicate detail names, and `addDetailUniqueName`.
- `TestSetupTearDown` detects test cases that call `setUp` or `tearDown` too many or too few times.
- `TestRunTwiceDeterminstic` and `TestRunTwiceNondeterministic` use sample-case scenarios to verify repeated runs either produce identical deterministic events or known nondeterministic event shapes.
- `TestSkipping` covers `skipTest`, custom `skipException`, old Python 2.6-style result fallback, method/class decorators from both testtools and unittest, and ensuring skipped decorators do not run `setUp`.
- `TestOnException` verifies `onException` and registered exception handlers.
- `TestPatchSupport` confirms `TestCase.patch` applies temporary attributes and restores or deletes them during cleanup.
- `TestTestCaseSuper` ensures `setUp`/`tearDown` cooperate with multiple inheritance via `super()`.
- `TestNullary` covers the small callable wrapper that stores arguments and exposes the wrapped function repr.
- `Attributes` plus `TestAttributes` cover `attr` and `WithAttributes`, proving tagged ids are sorted and stable.
- `TestDecorateTestCaseResult` verifies a wrapper test case that transforms the result before delegating and forwards attributes to the decorated case.

## Control Flow

Most tests synthesize inner `TestCase` subclasses, run them against `ExtendedTestResult`, `Python26TestResult`, `Python27TestResult`, `LoggingResult`, or `unittest.TestResult`, then assert event order and detail keys. This pattern exercises the full `TestCase.run` path: `startTest`, `setUp`, test method, `tearDown`, cleanups, outcome recording, `stopTest`, and tag restoration.

Cleanup tests intentionally raise exceptions from test bodies and cleanups to confirm that testtools converts multiple errors into one result event with multiple detail attachments. Skip tests branch through modern result objects and older result objects without skip support, proving fallback compatibility.

## State And Persistence Behavior

No repository state is persisted by this file. Runtime state is held in in-memory lists (`log`, `events`, `calls`), result double `_events`, generated detail dictionaries, class attributes on synthetic cases, and per-case counters used by unique factories. Patch tests mutate attributes on `self` but require restoration through cleanup. External state is limited to temporary details attached to test cases and result objects.

## Dependencies

The module depends heavily on the local testtools package: `TestCase`, `PlaceHolder`, `ErrorHolder`, `DecorateTestCaseResult`, `MultipleExceptions`, skip decorators, `clone_test_with_new_id`, `content`, `testcase`, `TracebackContent`, `text_content`, many matchers, `Nullary`, `WithAttributes`, `attr`, `TestSkipped`, result doubles, helper matchers, and sample-case scenario factories. Standard library dependencies include `doctest`, `pprint`, `sys`, `_thread`, and `unittest`.

## Integration Points

This is a central integration test for `testtools.testcase`, `testtools.runtest`, result adapters, matcher details, content objects, and skip compatibility with `unittest`. Failures here usually indicate a public behavior change affecting external users writing testtools-based test cases or consuming testtools result objects.

## Risks And Edge Cases

Key risks covered include lost cleanup errors, cleanup ordering regressions, incorrect skip fallback on older result objects, duplicate detail-name collisions, non-ASCII failure formatting, lifecycle misuse detection, repeated-run nondeterminism, tag leakage, patch restoration leaks, and wrappers failing to forward attributes or result hooks. The tests also guard against swallowing `KeyboardInterrupt` and `SystemExit` incorrectly.

## Test Signals

Strong test signals are exact result event sequences, expected detail-key sets, doctest-style traceback fragments, unique string outputs, skip reason storage, and restored object attributes after run completion. The suite is sensitive to line/path formatting in some traceback assertions but generally uses ellipses to tolerate implementation-version differences.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testcase.py -->
