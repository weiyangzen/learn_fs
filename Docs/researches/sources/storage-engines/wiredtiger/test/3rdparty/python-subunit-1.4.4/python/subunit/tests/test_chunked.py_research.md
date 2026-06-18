# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/tests/test_chunked.py

## Purpose

`test_chunked.py` verifies the HTTP-style chunked encoder/decoder used for multipart subunit details.

## Important APIs, Types, and Functions

`TestDecode` sets up a `BytesIO` output and `subunit.chunked.Decoder`. It tests close behavior, short/incomplete data, empty streams, combined writes, residue after terminal chunk, hex lengths, long 65,536-byte ranges, strict and non-strict newline handling, and malformed headers. `TestEncode` sets up `Encoder` and tests empty output, short buffering, hex length serialization, and large-write boundaries.

## Control Flow

Each test writes specific byte fragments and asserts either decoded output, returned residue, or `ValueError`. Encoder tests write bytes, close the encoder, and compare the exact serialized byte stream.

## State and Persistence Behavior

State is isolated per test in `BytesIO`. No filesystem state is used.

## Dependencies and Integration Points

It depends on `unittest`, `io.BytesIO`, `testtools.compat._b`, and `subunit.chunked`. It protects the detail parsing/serialization path used by `details.py` and `TestProtocolClient`.

## Risks and Test Signals

This file is the primary regression signal for chunk framing. It is especially useful for preventing Windows newline regressions, EOF handling mistakes, and accidental changes to the 65,536-byte flush threshold.
