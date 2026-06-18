# sources/object-store/rustfs/crates/rio/src/compress_index.rs

Purpose: this file defines the legacy compression `Index` and `TryGetIndex` trait used for seeking into compressed object streams. It can serialize/deserialize S2-style index frames and provide nearest compressed/uncompressed offsets for reads.

Important APIs and types: `TryGetIndex` defaults to no index. `Index` stores total uncompressed/compressed sizes, `IndexInfo` offset pairs, and estimated block size. `add` records monotonic offsets with a minimum uncompressed spacing of 1 MiB, updating an existing entry when the uncompressed offset is identical. `find` resolves positive or negative uncompressed offsets to the closest preceding index entry. `append_to`/`into_vec` write the skippable index frame; `load` and `load_stream` read it. `to_json` exposes a legacy JSON representation used by rio-v2 index conversion.

Control flow: serialization may call `reduce` to cap entries at `MAX_INDEX_ENTRIES`, writes marker bytes, `s2idx\0`, varint totals, estimated block size, entry count, optional uncompressed deltas, predicted compressed deltas, trailing size, and trailer. Deserialization validates marker, chunk length, optional legacy zero padding, header/trailer, sizes, entry count, flag, monotonic offsets, and returns any remaining bytes after the index.

State and persistence: `Index` is plain in-memory state until serialized into compressed object metadata/trailer bytes. The serialized frame is a persistent compatibility format and has legacy padding support.

Dependencies and integration points: uses `bytes`, `serde`, standard `Read + Seek`, and is imported by compression readers and rio-v2's S2 index bridge. `Index::to_json` is an internal compatibility bridge for new code.

Risks and test signals: varint encoding here is unsigned-style over `i64` and differs from rio-v2's signed zig-zag helpers, so cross-format assumptions require care. `find` uses a nonstandard `binary_search_by` shape for large indexes that should be monitored. Tests cover construction, add/find errors, reduction, JSON output, round-trip load, invalid marker rejection, and legacy zero-padded header acceptance.
