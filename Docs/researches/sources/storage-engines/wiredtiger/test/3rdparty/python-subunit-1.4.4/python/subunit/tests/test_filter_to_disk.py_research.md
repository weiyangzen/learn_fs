# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_filter_to_disk.py

## Purpose

`test_filter_to_disk.py` smoke-tests exporting a subunit v2 stream to disk.

## Important APIs, Types, and Functions

`SmokeTest.test_smoke` creates a temporary output directory, builds an in-memory v2 stream with `StreamResultToBytes`, writes a successful tagged test with attachment `fred`, runs `_to_disk.to_disk(['-d', output], stdin=stdin, stdout=stdout)`, and asserts file contents.

## Control Flow

The test constructs input, rewinds it, invokes the exporter, then checks `foo/test.json` and `foo/fred`.

## State and Persistence Behavior

It creates temporary filesystem state through `fixtures.TempDir`. The expected output is a JSON metadata file and an attachment file.

## Dependencies and Integration Points

It depends on `fixtures.TempDir`, `testtools.TestCase`, `FileContains`, `subunit._to_disk`, and `subunit.v2.StreamResultToBytes`. It validates `_to_disk` and the `subunit2disk` command's core implementation.

## Risks and Test Signals

The test covers the happy path only. It does not exercise path traversal, duplicate ids, multiple attachments, timestamps, or malformed input. Still, it is a direct signal that the exporter can consume v2 and write the documented disk layout.
