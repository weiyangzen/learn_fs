# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_run.py

## Purpose

`test_run.py` tests the `subunit.run` test runner integration.

## Important APIs, Types, and Functions

`TestSubunitTestRunner` verifies `SubunitTestRunner.run`, `.list`, and `run.main`. It defines nested `FailingTest` and `ExitingTest` fixtures for CLI behavior. Tests use `PlaceHolder`, `StreamResult`, and `ByteStreamToStreamResult` to inspect emitted v2 packets.

## Control Flow

Runner tests execute placeholder suites into `BytesIO`, decode the output stream, and assert timestamp and `exists` events. Listing error tests patch `run.list_test` or provide a loader with errors and assert `SystemExit(2)`. CLI tests call `run.main` with specific argv and stdout wrappers.

## State and Persistence Behavior

State is in in-memory streams and patched functions. No files are written.

## Dependencies and Integration Points

It depends on `testtools`, `unittest`, public `subunit.ByteStreamToStreamResult`, and `subunit.run`. It validates integration between testtools listing, stream result serialization, auto timing, and CLI exit policy.

## Risks and Test Signals

The tests assert that normal test failures do not cause `run.main` to exit, while execution errors can. They also check the v2 stream magic prefix. They do not cover buffering flags or `tb_locals`, but they exercise the runner's most important behavioral contract.
