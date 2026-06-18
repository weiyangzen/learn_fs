# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/__init__.py

## Purpose

`subunit/__init__.py` is the central public API for the Python Subunit package. It implements the original line-oriented subunit v1 protocol, exposes v2 stream adapters imported from `subunit.v2`, provides TAP conversion and tag filtering helpers, and supplies `unittest` integration classes for remote, isolated, and executable tests.

## Important APIs, Types, and Functions

Public exports include `TestProtocolServer`, `TestProtocolClient`, `ProtocolTestCase`, `RemotedTestCase`, `ExecTestCase`, `IsolatedTestCase`, `IsolatedTestSuite`, `run_isolated`, `TAP2SubUnit`, `tag_stream`, `TestResultStats`, `read_test_list`, `make_stream_binary`, and constants `PROGRESS_SET`, `PROGRESS_CUR`, `PROGRESS_PUSH`, and `PROGRESS_POP`. `__version__` is `(1, 4, 4, 'final', 0)`.

`TestProtocolServer` parses v1 byte lines into a `testtools`-extended result API. Its private parser states (`_OutSideTest`, `_InTest`, `_Reading*Details`) track whether a `test:` directive is active and whether the parser is consuming simple or multipart details. `TestProtocolClient` performs the reverse serialization: `startTest` writes `test:`, outcome methods write `error:`, `failure:`, `successful:`, `skip:`, `xfail:`, or `uxsuccess:`, and `_write_details` emits multipart details with chunked bodies.

`ProtocolTestCase` adapts a subunit byte stream to the callable `unittest` case/suite protocol. `RemotedTestCase` is a placeholder object representing a test that ran elsewhere. `TestResultStats` counts total, failed, skipped, passed, and seen tags. `TAP2SubUnit` converts TAP text into v2 status packets through `StreamResultToBytes`. `tag_stream` reads v2 packets with `ByteStreamToStreamResult` and rewrites `test_tags`.

## Control Flow

For v1 input, `ProtocolTestCase.run` wraps the target result in `TestProtocolServer` and feeds lines until EOF, then calls `lostConnection`. `_ParserState.lineReceived` identifies directive keywords, while `_InTest._outcome` validates that the outcome matches the current test id, switches back outside the test, or enters a details-reading state. Detail state delegates to `subunit.details` parsers and then reports the outcome to the decorated result.

For output, a test suite calls `TestProtocolClient.startTest`, one outcome method, and `stopTest`. Outcomes with traceback tuples become simple bracketed traceback details; outcomes with `details` dicts become multipart details, where each content item is serialized as content type, name, chunked bytes, and final bracket marker.

`run_isolated` forks, redirects child stdout to a pipe, runs the original `unittest` class method with `TestProtocolClient`, and has the parent parse the pipe through `TestProtocolServer`. `ExecTestCase` executes the script path stored in a test method docstring and parses stdout as subunit.

## State and Persistence Behavior

Parser state is kept in `TestProtocolServer._state`, `current_test_description`, and `_current_test`; malformed or truncated streams can synthesize `RemoteError` events on lost connection. `TestProtocolClient` writes directly to its binary stream and flushes at test boundaries. `run_isolated` uses OS pipes and forks, but persists no files. `tag_stream` and TAP conversion are streaming transformations and do not retain complete input beyond current TAP log/test state.

## Dependencies and Integration Points

The module depends on `testtools`, `iso8601`, `subunit.chunked`, `subunit.details`, and `subunit.v2`. It integrates with Python `unittest`, command-line filters in `subunit/filter_scripts`, and external TAP producers. Binary stream handling is important: `make_stream_binary` unwraps text streams and sets Windows file descriptors to binary mode.

## Risks and Test Signals

Key risks are protocol fidelity, byte/text boundary mistakes, and edge cases in v1 line parsing. `DiscardStream.write` has duplicated `pass` but no behavioral impact. `RemotedTestCase.run` calls `stopTest` twice, which looks suspicious and is worth preserving only because compatibility tests may depend on historic behavior. `run_isolated` assumes `os.fork`, so it is Unix-oriented. TAP parsing is regex based and handles common TAP constructs but not every TAP dialect.

The strongest test signals come from `test_subunit_filter.py`, `test_subunit_stats.py`, `test_subunit_tags.py`, `test_tap2subunit.py`, `test_run.py`, and the broader unlisted protocol tests in the same package. They exercise v1 parsing, v2 tag rewriting, TAP plan/missing-test behavior, stats accounting, and runner output decoding.
