<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs -->
# sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs

## Purpose
Provides the per-shard bitrot framing layer used by erasure-coded reads, writes, heals, and tests. Each shard block is stored as an optional hash prefix followed by shard bytes; readers verify the prefix before returning data, and writers compute and emit the prefix atomically with the data where possible.

## Important APIs, types, and functions
`BitrotReader<R>` wraps an async reader with `HashAlgorithm`, `shard_size`, scratch buffers, `skip_verify`, and an id used in mismatch logging. `BitrotReader::read` reads one framed shard block into caller-provided output and validates the hash unless disabled. `BitrotWriter<W>` wraps an async writer and writes one framed shard block at a time; `write` rejects oversized data and marks the writer finished after a short final shard. `write_all_vectored` is the low-level hash+data vectored write loop. `bitrot_shard_file_size` computes on-disk shard length including hash prefixes for HighwayHash S variants. `bitrot_verify` verifies a full shard stream against expected sizing. `CustomWriter` abstracts in-memory inline buffers and boxed async writers. `BitrotWriterWrapper` is the concrete writer wrapper used by encode/heal APIs, preserving inline-buffer extraction for tests and in-memory paths.

## Control flow
`BitrotWriter::write` returns immediately for empty input, rejects calls after a previous short write, verifies `buf.len() <= shard_size`, and marks `finished` if the block is shorter than a full shard. If the selected hash algorithm has a nonzero digest size, it hashes the data and writes hash plus data through `write_all_vectored`; otherwise it writes only data. `shutdown` flushes and shuts down the inner writer.

`BitrotReader::read` rejects output buffers larger than `shard_size`, reads the hash prefix exactly when the algorithm has a digest, then reads up to the requested output length. On hash mismatch it logs the reader id, read length, and requested length and returns `InvalidData`; otherwise it returns the number of bytes actually read. `bitrot_verify` compares the expected file size to `bitrot_shard_file_size`, then walks hash/data blocks, shrinking the final shard read to the remaining byte count and comparing each computed hash with the stored prefix.

`CustomWriter` implements `AsyncWrite` directly. Inline buffers append bytes to a `Vec<u8>` and report full writes, including vectored writes; `Other` delegates all write, flush, shutdown, and vectored behavior to the boxed writer. `BitrotWriterWrapper` owns a `BitrotWriter<CustomWriter>` and exposes `write`, `shutdown`, and `into_inline_data`.

## State and persistence behavior
The persistent format is a repeated sequence of `hash || shard_data` for algorithms with nonzero digest size, or raw shard data for `HashAlgorithm::None`. `bitrot_shard_file_size` models that format for the HighwayHash256S and HighwayHash256SLegacy variants. `BitrotWriter` enforces an append pattern where a short shard is terminal; this prevents writing more blocks after the last partial shard. `BitrotReader` is stateful over the underlying stream and consumes exactly one framed block per `read` call.

## Dependencies and integration points
Uses `bytes::Bytes`, `rustfs_utils::HashAlgorithm`, `tokio::io::{AsyncRead, AsyncWrite}`, `pin_project_lite`, `uuid::Uuid`, and `tracing`. `BitrotReader` is consumed by `decode::ParallelReader` and `heal`; `BitrotWriterWrapper` is consumed by `encode::MultiWriter` and `heal`. `CustomWriter::InlineBuffer` is an important test/in-memory integration point for heal and encode fast paths.

## Risks and test signals
The reader reads until EOF or the requested output length, so callers must pass the correct shard size for the current block, especially for final partial shards. `bitrot_verify` takes a `_want` parameter marked unused, suggesting an incomplete or legacy API contract. Size accounting differs by hash algorithm, so mismatching `HashAlgorithm` during read/write will desynchronize the stream. Vectored writes must handle partial writes correctly; `write_all_vectored` explicitly tracks hash and data offsets.

Tests cover hash read/write round trips, hash mismatch detection, no-hash operation, shutdown flush/shutdown counts, and vectored hash+data writes. Additional tests could exercise partial vectored writes and `bitrot_verify` with multi-block final-shard boundaries.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/ecstore/src/erasure_coding/bitrot.rs -->
