# sources/object-store/rustfs/crates/ecstore/src/bitrot.rs

Purpose: factory helpers for bitrot-verifying readers and bitrot-writing wrappers over inline data or disk-backed shard files.

Important APIs: `create_bitrot_reader` accepts optional inline bytes or disk, bucket/path, logical offset/length, shard size, checksum algorithm, verification flag, and zero-copy preference. It adjusts offset/length to include per-shard checksum overhead, then returns a `BitrotReader<Box<dyn AsyncRead...>>`. `create_bitrot_writer` chooses an inline buffer or disk-created file, adjusts expected length for checksum overhead, and returns `BitrotWriterWrapper`.

Control flow: reader creation prioritizes inline data. Disk reads use zero-copy when requested and local; success records zero-copy metrics, failure records fallback metrics and tries stream read, returning the original zero-copy error if fallback also fails.

State and persistence: inline mode stores data in memory; disk mode creates/reads shard files through `DiskStore`. Metrics are recorded through `rustfs_io_metrics`.

Dependencies and integration points: depends on disk APIs, erasure-coding bitrot wrappers, `Bytes`, `Cursor`, Tokio `AsyncRead`, and `rustfs_utils::HashAlgorithm`.

Risks: offset/length math must stay consistent with bitrot writer layout. Returning the original zero-copy error after fallback failure can hide the fallback error. Callers must pass valid shard sizes.

Test signals: async unit tests cover inline readers, zero-copy flag with inline data, inline offset correctness, missing data/disk behavior, inline writer data, and disk writer without disk error.
