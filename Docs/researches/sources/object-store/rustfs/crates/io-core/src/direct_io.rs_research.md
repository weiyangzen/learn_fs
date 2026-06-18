# sources/object-store/rustfs/crates/io-core/src/direct_io.rs

Purpose: aligned position-based file reader named `DirectIoReader`; comments explicitly clarify it is aligned `pread`/`read_at`, not true `O_DIRECT`.

Important APIs/types: `DirectIoError` reports unsupported platform/file, I/O string errors, or alignment failures. On Linux, `DirectIoReader::new(file, offset, size)` validates 512-byte offset and size alignment and builds an `AsyncRead` reader over a sync `std::fs::File`. Non-Linux builds expose the same type but constructor always returns `UnsupportedPlatform`.

Control flow: Linux `read_chunk` lazily fills an internal buffer from the requested position using `std::os::unix::fs::FileExt::read_at`, advances `pos` and `remaining`, then copies from internal buffer into caller buffers. `poll_read` repeatedly drains chunks into Tokio's `ReadBuf` and returns ready immediately.

State and persistence: reader state is per-instance file handle, current position, remaining byte count, internal buffer and buffer cursor. It does not mutate the underlying file offset.

Dependencies and integration: uses standard file APIs and Tokio `AsyncRead`; Linux-only re-export in `lib.rs`. It can be consumed wherever an async reader is expected, but it performs blocking reads in `poll_read`.

Risks: despite the type name, it does not open with `O_DIRECT` and does not ensure true direct I/O. `poll_read` performs synchronous disk I/O, which can block an async executor worker. Internal `Vec<u8>` is not guaranteed 512-byte memory-aligned, though comments mention buffer address alignment. Subtracting `remaining -= n` assumes `read_at` never returns more than requested aligned buffer length and remaining. Tests use `/dev/zero`, which is Linux-specific but guarded.

Test signals: unit test checks valid and invalid alignment on Linux and unsupported platform behavior elsewhere.
