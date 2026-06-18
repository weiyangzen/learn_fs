# sources/storage-engines/tikv/components/in_memory_engine/src/keys.rs

## Purpose

Defines the internal key/value byte wrapper and encoding scheme used by the in-memory engine skiplists. The format mirrors RocksDB internal-key ordering while preserving TiKV MVCC keys inside the user-key portion.

## Important APIs, Types, And Functions

`InternalBytes` wraps `bytes::Bytes` and an optional `Arc<MemoryController>`. When dropped with a controller set, it releases `bytes.len() + MEM_CONTROLLER_OVERHEAD`. It exposes constructors, raw byte accessors, `same_user_key_with`, `set_memory_controller`, and `memory_size_required`. Its `Ord` implementation compares all bytes except the final eight-byte internal suffix lexicographically, then compares the suffix as little-endian `u64` in descending order.

`ValueType` is the internal value/deletion tag with `Deletion = 0` and `Value = 1`. `VALUE_TYPE_FOR_SEEK` and `VALUE_TYPE_FOR_SEEK_FOR_PREV` match RocksDB seek conventions. `InternalKey` is the decoded view `{ user_key, v_type, sequence }`. `encode_internal_bytes`, `encode_key`, `encode_seek_key`, and `encode_seek_for_prev_key` append an eight-byte little-endian suffix containing `(seq << 8) | value_type`. `decode_key` reverses that encoding. Boundary helpers produce region start/end keys with or without MVCC timestamps, and `encoding_for_filter` builds a default-CF key for a MVCC prefix plus start timestamp.

## Control Flow

Keys inserted into skiplists are constructed from an MVCC user key plus sequence/value-type suffix. Default/write CF region scans use `encode_key_for_boundary_with_mvcc`, which appends `TimeStamp::max()` to the region boundary so all MVCC versions for the region start are included and the region end is excluded. Lock CF scans use `encode_key_for_boundary_without_mvcc`, because lock keys do not carry MVCC versions. GC filtering uses `encoding_for_filter` to find default-CF entries that correspond to write-CF `Put` records with external values.

## State And Persistence Behavior

`InternalBytes` is the memory-accounting ownership unit for skiplist keys and values. The source bytes are immutable and reference-counted, but memory quota is released when the wrapper drops, before the underlying `Bytes` allocation may actually be freed. The encoded keys are volatile in-memory representations; they are derived from RocksDB/MVCC keys and are not persisted by this module.

## Dependencies And Integration Points

Uses `bytes::{Bytes, BufMut}`, `engine_traits::CacheRegion`, `txn_types::{Key, TimeStamp}`, local `MemoryController`, and write-batch memory overhead constants. All storage, read, write, GC, load, cross-check, and delete-range code depends on this encoding for ordering and boundary correctness.

## Risks

The suffix format allows `u64::MAX` only as a sentinel; otherwise sequences must fit in 56 bits. `decode_key` unwraps value-type conversion and asserts minimum length, so corrupt internal keys panic. Ordering correctness depends on TiKV MVCC keys already being in memory-comparable encoded form. Memory accounting can be wrong if inserted keys/values do not have `memory_controller` set; `SkiplistHandle::insert` asserts this for normal writes.

## Test Signals

`test_compare_key` verifies value-type ordering, descending sequence ordering, MVCC timestamp ordering, and sentinel behavior. `test_encode_decode` checks little-endian suffix layout, sequence extraction, and value-type extraction. Test-only constructors generate deterministic user, region, MVCC, and value bytes for broader module tests.
