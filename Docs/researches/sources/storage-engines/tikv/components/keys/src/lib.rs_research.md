# sources/storage-engines/tikv/components/keys/src/lib.rs

## Purpose
`keys/src/lib.rs` defines TiKV's common key-space layout helpers. It builds and decodes local keys, raft log keys, region metadata keys, and data keys while preserving RocksDB lexicographic ordering.

## Important APIs, Types, and Functions
- Constants define key-space partitions: local prefix `0x01`, region raft/meta prefixes, raft/apply/snapshot suffixes, and data prefix `b'z'`.
- `raft_log_key`, `raft_state_key`, `apply_state_key`, `snapshot_raft_state_key`, and prefix helpers construct fixed-width big-endian keys.
- `raft_log_index`, `decode_raft_log_key`, `decode_raft_key`, `decode_region_raft_key`, and `decode_region_meta_key` validate and decode persisted keys.
- `data_key`, `data_key_with_buffer`, `data_end_key`, `origin_key`, and `origin_end_key` translate raw user keys into TiKV encoded data-space keys.
- `enc_start_key` and `enc_end_key` convert initialized `Region` bounds to encoded data-space bounds and assert peers exist.
- `next_key` computes the immediate lexicographic successor, returning empty for no successor.
- `Error` reports invalid raft or region keys using `log_wrappers::Value`.

## Control Flow
Encoding functions allocate fixed arrays or vectors and write region ids/log indexes with big-endian order. Decoders first validate exact lengths, prefixes, and suffixes, then read ids. Data-key functions prepend or strip `DATA_PREFIX`, with empty end keys mapped to `DATA_MAX_KEY`.

## State and Persistence Behavior
The functions define persisted RocksDB key formats. Big-endian region ids and log indexes preserve sort order. `data_end_key` maps an unbounded raw end key to the exclusive upper data boundary, and `origin_end_key` reverses that mapping.

## Dependencies and Integration Points
The crate is used across raftstore, engine, backup/import, and region-routing code that needs stable keys. It depends on `kvproto::metapb::Region`, `byteorder`, and logging wrappers for safe key display.

## Risks
Any incompatible change to constants or fixed-width layout can make existing RocksDB data unreadable. `origin_key` and region boundary helpers assert on invalid input and can panic if callers pass unencoded keys or uninitialized regions. `next_key` returning empty means "unbounded/no successor" in several range contexts, so consumers must distinguish it from a real empty key.

## Test Signals
Inline tests verify region key prefixing, lexicographic sort order, raft log decoding errors, data key validation, initialized-region assertions via `panic_hook`, and end-key encoding.
