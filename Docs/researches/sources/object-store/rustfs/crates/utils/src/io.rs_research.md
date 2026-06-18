# sources/object-store/rustfs/crates/utils/src/io.rs

## Purpose
Provides async IO helpers and unsigned varint encoding/decoding utilities used by RustFS streaming and binary metadata code.

## Important APIs, Types, And Functions
`write_all` loops over `AsyncWrite::write` until all bytes are written or the writer returns zero, returning the total bytes written. `read_full_or_eof` reads into a buffer until full, EOF, or error, returning `None` for EOF before any bytes and `Some(n)` for partial or full reads. `read_full` wraps that helper and maps initial EOF to `UnexpectedEof`. `put_uvarint`, `put_uvarint_len`, and `uvarint` implement Go-style unsigned varint encode/decode with overflow and incomplete-buffer signaling.

## Control Flow And State
The async read/write helpers are stateless loops over caller-owned reader/writer values. `read_full_or_eof` preserves `InvalidData` errors after partial reads but wraps other post-partial errors as `UnexpectedEof`. `uvarint` accumulates seven-bit chunks and returns `(0, 0)` for incomplete data or `(0, negative_count)` on overflow.

## Dependencies And Integration Points
Depends on `tokio::io::{AsyncRead, AsyncReadExt, AsyncWrite, AsyncWriteExt}`. Exported through `lib.rs` under the `io` feature; `retry.rs` is only compiled when both `net` and `io` features are enabled.

## Risks And Test Signals
`write_all` returns short success if a writer yields `Ok(0)`, which differs from Tokio's usual `write_all` error semantics and may hide stalled writers. `read_full` intentionally allows short reads after some data, despite its name. Tests cover exact, short, empty, large reads, partial writes, and varint zero/max/overflow/incomplete cases.
