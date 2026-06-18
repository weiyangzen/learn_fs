# sources/object-store/rustfs/crates/rio-v2/src/compress_reader.rs

Purpose: this file implements rio-v2 async S2-compatible compression and decompression readers. It is designed to emit MinIO/S2 framed streams using `minlz`, maintain a seek index for large streams, and support encrypted-object padding alignment.

Important APIs and types: `CompressReader<R>` wraps an `AsyncRead`, buffers up to a block size (default 1 MiB), writes the `S2sTwO` stream identifier once, emits compressed or uncompressed framed chunks with CRC, updates a `rustfs_rio::Index`, and exposes the index through `TryGetIndex` only after more than 8 MiB uncompressed data. `with_encrypted_padding` appends a random padding frame to align the compressed output to 256-byte boundaries. `DecompressReader<R>` parses S2 chunk headers incrementally, accepts `S2sTwO` and `sNaPpY` identifiers, decodes compressed/uncompressed chunks, verifies CRC, skips index/padding/skippable chunks, and returns plaintext bytes across async poll boundaries.

Control flow: both readers first drain any buffered output, then resume their current read state. Compression accumulates a full block unless EOF occurs, chooses compressed form only if it saves enough space, writes a 24-bit chunk length and 4-byte checksum, then copies as much as the caller's `ReadBuf` can accept. Decompression persists header/body read progress, handles short reads and `Poll::Pending`, validates chunk type, and keeps decoded output in a buffer until consumed.

State and persistence: state is entirely in-reader memory: output buffers, read buffers, written byte counters, uncompressed counters, stream-header flag, optional padding multiple, and `Index`. The emitted byte stream is persistent object data, so chunk framing and CRC behavior are compatibility-critical.

Dependencies and integration points: uses `minlz::{Encoder, decode, crc}`, `tokio::io::AsyncRead`, `pin_project_lite`, `rustfs_utils::CompressionAlgorithm` for API shape, and rio traits for ETag/hash/index delegation. It integrates with rio-v2 encryption because encrypted-padding alignment affects encrypted object layout.

Risks and test signals: risks include 24-bit length overflows, accepting malformed skippable frames too broadly, random padding nondeterminism, and index offset accuracy around the stream header. Unit tests cover minlz decode compatibility, small/large/random round-trips, erasure-boundary sizes, pending sources, first-read output, resumed chunk bodies, concatenated streams, encrypted padding, and small-stream index suppression.
