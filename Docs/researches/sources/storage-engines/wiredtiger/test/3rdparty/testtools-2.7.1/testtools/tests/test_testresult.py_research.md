<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py -->
# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py

## Purpose

This module is the main contract and regression suite for testtools result classes, result decorators, stream result conversion, routing, summaries, non-ASCII traceback rendering, per-test callback results, tagging, and timestamping. It defines reusable contract mixins for result behavior and applies them to many concrete result implementations.

## Important APIs, Types, And Functions

- Factory helpers create representative passing, failing, erroring, mismatching, and unexpectedly successful tests plus `make_exception_info`.
- `TestControlContract`, `Python26Contract`, `Python27Contract`, `TagsContract`, `DetailsContract`, `FallbackContract`, and `StartTestRunContract` describe expected behavior for result control, success/failure accounting, skip/xfail/uxsuccess, tag scope, details API, fallback policy, and run reset behavior.
- Concrete contract classes apply those contracts to `TestResult`, `MultiTestResult`, `TextTestResult`, `ThreadsafeForwardingResult`, `ExtendedTestResult`, Python 2.6/2.7 doubles, Twisted doubles, `ExtendedToOriginalDecorator`, `ExtendedToStreamDecorator`, `StreamToExtendedDecorator`, and `TestResultDecorator`.
- `TestStreamResultContract` exercises `StreamResult.status` across file and non-file parameter power sets; derived classes apply it to stream decorators and routers.
- `TestDoubleStreamResultEvents`, `TestCopyStreamResultCopies`, `TestStreamTagger`, `TestStreamToDict`, `TestExtendedToStreamDecorator`, `TestResourcedToStreamDecorator`, `TestStreamFailFast`, and `TestStreamSummary` validate stream-event semantics.
- `TestTestResult`, `TestMultiTestResult`, `TestTextTestResult`, and `TestThreadSafeForwardingResult` cover classic result behavior, fan-out, text output, and atomic forwarding under concurrency.
- `TestMergeTags`, `TestStreamResultRouter`, and `TestStreamToQueue` cover tag-delta merging, route-code/test-id routing, queue event serialization, and route prefix composition.
- `TestExtendedToOriginalResultDecoratorBase` plus outcome-specific subclasses validate conversion from extended details APIs to older result APIs.
- `TestNonAsciiResults` and `TestNonAsciiResultsWithUnittest` create temporary modules in varied encodings to verify traceback and exception text rendering.
- `TestDetailsToStr`, `TestByTestResultTests`, `TestTagger`, and `TestTimestampingStreamResult` cover detail stringification, one-callback-per-test summaries, per-test tag injection, and automatic timestamp insertion.

## Control Flow

The file begins with reusable behavior contracts and then instantiates them for each result implementation. Many tests call `startTestRun`, mutate tags or time, run synthetic tests, emit outcome methods, and assert the resulting state or event logs. Stream tests call `status` directly with combinations of `test_id`, `test_status`, `test_tags`, `runnable`, `file_name`, `file_bytes`, `eof`, `mime_type`, `route_code`, and `timestamp`.

Adapter tests branch on target capability: Python 2.6-style results receive fewer calls and map unsupported outcomes to success or failure; Python 2.7-style results receive skip/expected-failure support; extended results preserve detail dictionaries. The non-ASCII tests create temporary modules, import them, run generated cases through `TextTestResult` or `unittest.TextTestRunner`, and inspect the output stream.

## State And Persistence Behavior

Runtime state is held in result object fields such as `shouldStop`, `failfast`, `testsRun`, `current_tags`, skip reason maps, stream event lists, queues, timestamp fields, and summary lists. Temporary files and importable modules are created under `tempfile.mkdtemp` in `TestNonAsciiResults` and removed through cleanups; `sys.path` and `sys.modules` are also restored through cleanups. `TestTestResult.test_now_datetime_now` temporarily patches `testresult.real.datetime` and restores it.

## Dependencies

The module uses many testtools exports: result classes/decorators, stream classes, `PlaceHolder`, `TestCase`, `TestControl`, `TestByTestResult`, content helpers, compatibility helpers, matchers, result doubles, and `_details_to_str`, `_merge_tags`, and `utc` from `testtools.testresult.real`. Standard dependencies include `codecs`, `datetime`, `doctest`, `io`, `itertools`, `os`, `platform`, `queue`, `re`, `shutil`, `sys`, `tempfile`, `threading`, and `unittest.TestSuite`. Optional `testresources` is imported with `try_import` and gates resource-stream tests.

## Integration Points

This file validates the contract among classic unittest-style results, extended testtools results, stream results, subunit-like event flows, routing, and queue transport. It is a key guard for users that bridge testtools into old unittest consumers, Twisted/subunit style result consumers, or concurrent runners requiring atomic per-test event forwarding.

## Risks And Edge Cases

Major risks include incompatible fallback mappings, tag leakage between tests, failure to reset result state at `startTestRun`, incorrect failfast behavior, empty attachments being dropped or misreported, malformed MIME handling, in-progress stream tests not failing at run end, route-code prefix consumption mistakes, queue route composition errors, Unicode/encoding regressions in tracebacks, temporary import pollution, and broken timestamp injection.

## Test Signals

Signals include exact `_events` tuples, `wasSuccessful()` state, `shouldStop`, skip reason maps, stream summaries, queue dictionaries, rendered text output fragments, detail stringification output, per-test callback dictionaries, and timestamp type/value assertions. The encoding tests are especially valuable for platform compatibility but are intentionally tolerant around implementation-specific syntax-error formatting.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/tests/test_testresult.py -->
