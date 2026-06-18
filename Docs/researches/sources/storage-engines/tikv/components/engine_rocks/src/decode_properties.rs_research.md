<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs -->
# sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs

Purpose: provides shared binary decoding primitives for RocksDB user-collected table properties.

Important APIs/types/functions: `IndexHandle`, `IndexHandles`, `IndexHandles::{new, into_map, add, encode, decode}`, and `DecodeProperties::{decode, decode_u64, decode_handles}`.

Control flow: `IndexHandles::encode` writes a sequence of key length, key bytes, handle size, and handle offset using TiKV number encoding. `decode` reads until the buffer is exhausted. `DecodeProperties` implementations expose keyed property blobs and typed helpers.

State and persistence behavior: the encoded format is stored in SST user properties and must remain compatible for range and MVCC property readers.

Dependencies/integration: used by `properties.rs` and `mvcc_properties.rs`; integrates RocksDB `UserCollectedProperties` with TiKV codec APIs.

Risks: malformed lengths can produce decode errors; duplicate keys overwrite earlier handles because decoding inserts into a `BTreeMap`. Format changes would break old SST metadata unless fallback logic is maintained.

Test signals: no direct tests here; exercised by range and MVCC property tests that encode/decode handles.
<!-- END_FILE_RESEARCH: sources/storage-engines/tikv/components/engine_rocks/src/decode_properties.rs -->
