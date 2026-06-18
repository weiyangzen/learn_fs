# sources/object-store/rustfs/crates/rio/src/compress_reader.rs

Purpose: this file implements the legacy async block compression and decompression readers used by `rustfs-rio`. It frames compressed blocks with a custom 8-byte header, original-length varint, and CRC32 checksum.

Important APIs and types: `CompressReader<R>` wraps an `AsyncRead`, buffers 1 MiB blocks by default, compresses each block with `rustfs_utils::compress::compress_block`, updates a legacy `Index`, and exposes it through `TryGetIndex`. `DecompressReader<R>` reads the custom block header, body, original length varint, decompresses or passes through uncompressed blocks, verifies decompressed length and CRC32, and yields plaintext across async polls.

Control flow: compression drains buffered output first, then fills `temp_buffer` until block size, EOF, or a pending inner read with partial data. It builds a compressed block via `build_compressed_block`, increments written/uncompressed counters, adds an index entry, and copies to the caller buffer. Decompression persists header-read and body-read progress, interprets type `0x00` compressed, `0x01` uncompressed, and `0xff` end, validates the decoded length from `uvarint`, and reports invalid type, decompression errors, length mismatch, or CRC mismatch as `InvalidData`.

State and persistence: per-reader state includes buffers, positions, done flags, block size, algorithm, index, and read progress. The persistent format is the custom frame sequence. The file delegates reader capabilities to the wrapped reader via `delegate_reader_capabilities_generic_no_index!`.

Dependencies and integration points: depends on `compress_index::{Index, TryGetIndex}`, `rustfs_utils` compression/uvarint helpers, `crc-fast`, `tokio::io`, and `pin_project_lite`. rio-v2 keeps these public traits but replaces the wire format for MinIO-compatible paths.

Risks and test signals: the decompressor reads `compressed_buf[0..16]` for varint without first checking the buffer has 16 bytes, so malformed tiny blocks can panic rather than return an error. Pending behavior after partial header/body reads is stateful and important. Index entries are added after incrementing totals, so offset interpretation differs from rio-v2's S2 stream-header-aware indexing. Tests cover gzip/deflate/default round-trips, empty data, and multi-megabyte random data.
