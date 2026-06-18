# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol.py

## Purpose

This file is the broad regression suite for python-subunit's original text protocol and adjacent unittest integration helpers. It validates the public imports exposed by `subunit`, the line-oriented `TestProtocolServer` parser, the `TestProtocolClient` serializer, remoted test objects, child-process execution, and process isolation helpers. The tests exercise both old stdlib-like `TestResult` behavior and testtools extended result behavior, which is important because subunit sits between external test producers and many generations of Python result consumers.

## Important APIs, Types, and Test Fixtures

- `details_to_str(details)` uses `testtools.TestResult()._err_details_to_string` to normalize detail dictionaries into the string form expected by legacy error/failure tuples.
- `TestHelpers` covers `subunit._unwrap_text` for text files, `io.FileIO`, and `io.BytesIO`, ensuring binary stream access is preserved when possible.
- `TestTestImports` asserts the package-level API exports `DiscardStream`, `ExecTestCase`, `IsolatedTestCase`, `ProtocolTestCase`, `RemotedTestCase`, `RemoteError`, `TestProtocolClient`, and `TestProtocolServer`.
- `TestProtocolServerForward`, `TestTestProtocolServerPipe`, `TestTestProtocolServerStartTest`, `TestTestProtocolServerPassThrough`, and `TestTestProtocolServerLostConnection` drive `TestProtocolServer.lineReceived`, `readFrom`, and `lostConnection`.
- `TestInTestMultipart`, `TestTestProtocolServerAddError`, `TestTestProtocolServerAddFailure`, `TestTestProtocolServerAddxFail`, `TestTestProtocolServerAddunexpectedSuccess`, `TestTestProtocolServerAddSkip`, and `TestTestProtocolServerAddSuccess` cover outcome parsing, bracketed details, multipart details, quoted closing brackets, and compatibility shims for result methods that may not support extended details.
- `TestTestProtocolServerProgress`, `TestTestProtocolServerStreamTags`, and `TestTestProtocolServerStreamTime` cover stream metadata directives.
- `TestRemotedTestCase` and `TestRemoteError` validate identity, formatting, equality, and non-runnable remote error behavior.
- `TestExecTestCase`, `DoExecTestCase`, `TestIsolatedTestCase`, and `TestIsolatedTestSuite` cover subprocess and fork-isolated execution helpers.
- `TestTestProtocolClient` validates serialized text protocol output for start, success, failure, error, skip, expected failure, unexpected success, progress, time, tags, Unicode test IDs, and multipart `testtools.content.Content` details.

## Control Flow and State Behavior

The server tests model a text protocol state machine. A `test` or `testing` line creates a `RemotedTestCase` and emits `startTest`. Outcome lines such as `success`, `successful`, `failure`, `error`, `skip`, `xfail`, and `uxsuccess` terminate the current test with the appropriate result event and `stopTest`. When an outcome line opens a bracketed detail block, the server switches into detail-reading mode until a bare closing `]` is received; an escaped bracket is represented by a leading-space line such as ` ]`. Multipart detail mode delegates to `subunit.details.MultipartDetailsParser`.

The pass-through tests establish that lines not recognized in the current parser state are written to the configured stream, but that detail parsers retain control while inside a detail block. `lostConnection` tests verify terminal recovery: no started test means no event, a started but unfinished test becomes an `addError` with a remote lost-connection message, and an interrupted outcome/detail block reports that the connection was lost during that outcome's report.

The client tests cover the reverse flow: `TestProtocolClient` receives unittest/testtools result calls and writes text protocol lines to a byte stream. Simple outcomes produce one-line records; errors and failures with exceptions produce bracketed tracebacks; extended detail dictionaries produce multipart records. Progress, time, and tags emit stream-level directives immediately. `stopTest` intentionally emits no bytes because the v1 protocol treats outcome lines as test terminators.

State is mostly in-memory: `BytesIO` captures serialized streams, testtools result doubles capture `_events`, and class-level boolean flags in isolated test fixtures verify that child process mutations do not persist in the parent. Temporary files are used only to exercise `_unwrap_text` and are removed via cleanup hooks.

## Dependencies and Integration Points

The suite depends on `unittest`, `testtools`, `iso8601`, and the vendored `subunit` package. It imports testtools compatibility helpers (`_b`, `_u`), content types, matchers, and result doubles for Python 2.6/2.7 style compatibility even though this vendored copy targets Python 3. The subprocess execution tests rely on sibling sample scripts in the `subunit.tests` package and on POSIX for fork-based isolation tests. The suite integrates directly with public subunit APIs and with internal constants from `subunit.tests` that normalize remote exception representations across testtools versions.

## Risks and Maintenance Signals

- The tests encode precise textual protocol bytes, including whitespace and bracket escaping; parser or serializer refactors can break compatibility with existing subunit consumers.
- Several assertions allow alternate traceback representations because testtools changed traceback formatting. Future dependency changes may require similar compatibility branches.
- Outcome compatibility differs by result implementation: old Python-style results may map `xfail` to success or `uxsuccess` to failure, while extended testtools results preserve richer events and details.
- Isolation tests are skipped outside POSIX, so regressions in fork-based behavior may not be detected on Windows.
- `TestTestProtocolServerPipe.test_non_test_characters_forwarded_immediately` and some debug/count tests are placeholders, indicating incomplete coverage for immediate forwarding and child-process count behavior.

## Test Signals

This file is itself the test signal for the v1 subunit protocol. Strong signals include full start/outcome/stop event order assertions, passthrough byte assertions, lost-connection recovery assertions, Unicode serialization, multipart detail serialization, progress/time/tag directives, and process-isolation checks. It should be run with the rest of python-subunit's test suite whenever protocol parsing, result adaptation, or packaging of sample scripts changes.
