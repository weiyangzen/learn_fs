# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/filter_scripts/subunit_2to1.py

## Purpose

`subunit_2to1.py` converts subunit v2 input into the older v1 textual protocol.

## Important APIs, Types, and Functions

`main()` constructs `ByteStreamToStreamResult` for input, `TestProtocolClient(sys.stdout)` for v1 output, wraps it with `StreamToExtendedDecorator`, and uses `StreamResultRouter` to send global non-test file packets to `CatFiles(sys.stdout)`.

## Control Flow

The v2 parser emits stream events. `StreamToExtendedDecorator` translates test events to extended result calls, which `TestProtocolClient` serializes as v1 directives. Router rules divert events with `test_id=None` to `CatFiles` so global attachments become raw stdout content.

## State and Persistence Behavior

This is a streaming stdout transformation and persists no files. The output is byte-oriented even though it is passed through `sys.stdout`.

## Dependencies and Integration Points

It depends on `testtools.StreamResultRouter`, `StreamToExtendedDecorator`, `subunit.ByteStreamToStreamResult`, `TestProtocolClient`, shared `find_stream`, and `CatFiles`.

## Risks and Test Signals

The v2 protocol can represent global attachments and richer stream status than v1; conversion may lose metadata. A practical test is converting v2 streams with successful, failing, skipped, tagged, and global stdout events and reparsing the result with `ProtocolTestCase`.
