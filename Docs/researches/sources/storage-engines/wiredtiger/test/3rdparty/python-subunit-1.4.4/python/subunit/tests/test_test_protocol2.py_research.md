# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_test_protocol2.py

## Purpose

This file tests python-subunit's v2 binary protocol adapters. It verifies that `StreamResultToBytes` conforms to the testtools `StreamResult` contract and emits stable binary packets, and that `ByteStreamToStreamResult` parses those packets back into `StreamResult.status` events while safely handling non-subunit bytes, malformed packets, bad checksums, invalid UTF-8, and optional property-based fuzzing.

## Important APIs, Types, and Constants

- `CONSTANT_ENUM`, `CONSTANT_INPROGRESS`, `CONSTANT_SUCCESS`, `CONSTANT_UXSUCCESS`, `CONSTANT_SKIP`, `CONSTANT_FAIL`, `CONSTANT_XFAIL`, `CONSTANT_EOF`, `CONSTANT_FILE_CONTENT`, `CONSTANT_MIME`, `CONSTANT_TIMESTAMP`, `CONSTANT_ROUTE_CODE`, `CONSTANT_RUNNABLE`, and `CONSTANT_TAGS` are golden binary packets for deterministic wire compatibility checks.
- `TestStreamResultToBytesContract` mixes in `TestStreamResultContract` and returns `subunit.StreamResultToBytes(BytesIO())`.
- `TestStreamResultToBytes` checks varint number encoding boundaries, volatile packet-length boundaries, known status encodings, route codes, runnable flags, tags, timestamps, file content, MIME type, EOF, and unknown status rejection.
- `TestByteStreamToStreamResult` checks conversion of raw bytes to file-content events, parsing of valid v2 packets, parser-error status events for corrupt packets, route+file combined packets, and an optional Hypothesis binary fuzz test when `hypothesis` is importable.
- Helper methods `check_events`, `check_event`, and `_event` build expected `StreamResult` event tuples for compact parser assertions.

## Control Flow and State Behavior

The encoder tests call `StreamResultToBytes.status(...)` with one or more status fields and inspect the resulting `BytesIO` bytes. Numeric encoding is tested at every variable-length boundary: 1-byte values up to 63, 2-byte values up to 16383, 3-byte values up to 4194303, and 4-byte values up to 1073741823. Packet length tests focus on boundaries where the packet length field itself changes size, preventing off-by-one regressions.

The decoder tests feed `BytesIO` streams to `ByteStreamToStreamResult(...).run(result)`. When `non_subunit_name` is set, bytes outside v2 packets become `status(file_name=<name>, file_bytes=<byte>)` or aggregated file-content events. A signature-like byte sequence inside a multibyte UTF-8 character must not be misread as a subunit packet start. When `non_subunit_name` is omitted, the first non-subunit byte raises an exception and leaves the unread remainder in the source stream.

Malformed packet tests assert that parse failures are reported as two synthetic `subunit.parser` events: one attaches the packet bytes as `application/octet-stream`, and one reports `test_status='fail'` with a text parser error. This keeps parser corruption visible in the result stream rather than crashing successful decoding of surrounding content. The optional Hypothesis test feeds arbitrary binary data through the decoder to assert complete stream consumption without requiring all bytes to be valid subunit.

## Dependencies and Integration Points

The tests use `BytesIO`, `datetime`, `iso8601.UTC`, `testtools.TestCase`, `testtools.matchers.Contains` and `HasLength`, `StreamResult` doubles, and `TestStreamResultContract`. Hypothesis is optional; when unavailable, the property test is not defined. The subject APIs are exposed through `subunit.StreamResultToBytes` and `subunit.ByteStreamToStreamResult`, which are implemented in `python/subunit/v2.py` and integrated with testtools `StreamResult` consumers.

## Risks and Maintenance Signals

- Golden binary constants make wire-format changes explicit, but they also mean benign ordering changes, especially tag set order, must be handled deliberately. The tag test accepts either ordering.
- Packet length and varint boundaries are high-risk because length includes signature, flags, encoded length, body, and CRC. The tests directly protect boundary calculations.
- Parser error reporting is part of observable behavior; changing exceptions into raised errors would break downstream tooling that expects parser failures as status events.
- Hypothesis coverage is conditional, so environments without the optional test dependency lose fuzz-style assurance over arbitrary binary streams.
- The tests validate selected malformed packet cases, not every invalid flag combination or truncation path.

## Test Signals

This file is the focused regression suite for subunit v2 byte compatibility. The strongest signals are golden packet equality, round-trip parser event equality, error-event emission for CRC and structural failures, UTF-8 edge cases, and the testtools `StreamResult` contract mixin.
