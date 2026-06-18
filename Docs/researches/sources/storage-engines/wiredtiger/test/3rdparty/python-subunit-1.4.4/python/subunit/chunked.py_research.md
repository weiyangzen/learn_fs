# sources/storage-engines/wiredtiger/test/3rdparty/python-subunit-1.4.4/python/subunit/chunked.py

## Purpose

`chunked.py` implements HTTP-style chunked byte encoding and decoding used by the subunit v1 multipart detail format.

## Important APIs, Types, and Functions

`Decoder(output, strict=True)` accepts encoded bytes via `write()` and writes decoded body bytes to `output`. It exposes `close()` to detect incomplete streams. Internal states are `_read_length`, `_read_body`, and `_finished`. `Encoder(output)` buffers small writes and serializes chunks through `write()`, `flush(extra_len=0)`, and `close()`.

## Control Flow

The decoder buffers writes, scans hex length lines until newline, validates CRLF in strict mode, then copies exactly `body_length` bytes to the output. A zero-length chunk switches to `_finished` and any bytes after the terminal chunk are returned as residue. The encoder buffers until a write would reach 65,536 bytes; it then flushes a hex length header, buffered bytes, and the large write body. `close()` writes the final `0\r\n`.

## State and Persistence Behavior

Both classes are in-memory stream adapters. `Decoder` keeps `buffered_bytes`, `body_length`, and state function references. `Encoder` keeps a byte list and `buffer_size`. Persistence occurs only through the caller's output stream.

## Dependencies and Integration Points

The only external helper is `testtools.compat._b` for byte literals. `subunit.details.MultipartDetailsParser` uses `Decoder`, and `TestProtocolClient._write_details` uses `Encoder`.

## Risks and Test Signals

Risks center on strict CRLF parsing, residual bytes after terminal chunks, incomplete stream detection, and memory behavior for many small writes. `test_chunked.py` validates empty, short, long, hex, combined, and oversized chunks; strict versus non-strict newline handling; residue after EOF; write-after-finish errors; and encoder buffering boundaries.
