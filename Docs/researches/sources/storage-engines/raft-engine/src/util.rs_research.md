# sources/storage-engines/raft-engine/src/util.rs

Purpose: this file provides general utilities shared across raft-engine: binary size formatting/parsing, saturating time elapsed, CRC32, reversible u64 hashing, LZ4 block compression helpers, a generic factory trait, and alignment helpers.

Important APIs and types: binary unit constants `B`, `KIB`, `MIB`, `GIB`, `TIB`, and `PIB`; `ReadableSize` with constructors `kb`, `mb`, `gb`, `as_mb`, arithmetic ops, `Display`, `FromStr`, serde serialize/deserialize; `InstantExt::saturating_elapsed`; `crc32`; `hash_u64` and `unhash_u64`; `lz4::append_compress_block` and `lz4::decompress_block`; `Factory<Target>`; `round_up` and `round_down`.

Control flow: `ReadableSize::from_str` splits an ASCII string into numeric and unit components, supports decimal/scientific notation, maps accepted binary units, and truncates `f64 * unit` to `u64`. Serialization writes the display string; deserialization accepts integers or strings. LZ4 compression appends a 4-byte little-endian decoded length followed by compressed bytes to the same buffer after a `skip` prefix. Decompression reads the length, allocates the decoded buffer, calls `LZ4_decompress_safe`, and validates the decoded size. `hash_u64`/`unhash_u64` are SplitMix64 permutation and inverse.

State and persistence behavior: no persistent state. The encoded LZ4 block format is persisted when log batches choose compression, so its layout `{decoded_len | compressed content}` is a storage compatibility concern. `ReadableSize` string forms are persisted in TOML configs.

Dependencies and integration points: depends on `crc32fast`, `serde`, `lz4_sys`, and crate `Error`/`Result`. `ReadableSize` is used by config, stress CLI parsing, benchmarks, and display. `InstantExt` is used by metrics. `hash_u64` is used to shard memtable accessors. LZ4 helpers are used by log-batch compression/decompression paths.

Risks and invariants: `ReadableSize::from_str` accepts signs and exponent notation in the numeric substring; negative parsed values cast through `f64` to `u64` can be surprising if not rejected by caller expectations. Display prints `0KiB` for zero. LZ4 compression rejects content longer than `i32::MAX`; decompression treats non-empty inputs shorter than or equal to four bytes as corruption. `round_up` uses `div_ceil` and will panic on zero alignment.

Test signals: unit tests cover readable-size arithmetic, TOML serialization/deserialization, valid/invalid parse cases including scientific notation, hash/unhash inversion, rounding, and LZ4 basic compression/decompression including empty input.
