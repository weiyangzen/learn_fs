# sources/storage-engines/rocksdb/table/block_based/data_block_hash_index.h

## Purpose
Defines RocksDB's experimental hash index embedded inside data blocks to reduce CPU cost for point lookups. The header documents the on-disk block layout extension and declares the builder and reader used by data-block construction and lookup.

## Important APIs, Types, And Functions
Constants `kNoEntry`, `kCollision`, `kMaxRestartSupportedByHashIndex`, `kMaxBlockSizeSupportedByHashIndex`, and `kDefaultUtilRatio` define encoding limits. `DataBlockHashIndexBuilder` exposes `Initialize`, `Valid`, `Add`, `Finish`, `Reset`, and `EstimateSize`. `DataBlockHashIndex` exposes `Initialize`, `Lookup`, and `Valid`.

## Control Flow
Callers create a builder, initialize it with a utilization ratio, add keys with their data-block restart indexes, check `Valid`, and append bytes through `Finish`. Readers detect hash-index presence from the data-block footer, initialize the `DataBlockHashIndex` over serialized block bytes, then ask `Lookup` for the probable restart interval before searching within the interval.

## State And Persistence Behavior
The persistent format is `HASH_IDX: [bucket bytes][fixed16 num_buckets]` appended before the data-block footer. Bucket bytes contain either a restart index, `kNoEntry`, or `kCollision`. The builder maintains transient hash/restart pairs and an estimated bucket count; only `Finish` emits bytes.

## Dependencies And Integration Points
The header depends on `rocksdb/slice.h` and is consumed by block builder/reader code and by tests. It is explicitly data-block-only and not intended for table index blocks or metadata blocks.

## Risks And Edge Cases
The format supports at most 253 restart intervals because bucket entries are `uint8_t` and reserve two sentinel values. Block offsets are `uint16_t`, so blocks at or above 64KiB cannot use this index. Collision and missing-entry handling must preserve correctness by falling back to normal restart-interval search.

## Test Signals
Friend access supports the small builder test. Coverage checks format sizing, restart limits, block-size limits, and lookup correctness with existing and non-existing keys.
