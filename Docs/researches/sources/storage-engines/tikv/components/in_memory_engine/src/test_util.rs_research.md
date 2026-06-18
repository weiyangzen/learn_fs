# sources/storage-engines/tikv/components/in_memory_engine/src/test_util.rs

## Purpose

This file provides test helpers for constructing MVCC data in the in-memory skiplist and RocksDB, plus a helper for building minimal `Region` metadata. It keeps read/write tests focused on behavior rather than repetitive encoding and memory-controller setup.

## Important APIs, Types, And Functions

- `put_data` inserts a write-CF record and, when needed, its default-CF value into skiplist handles.
- `put_data_with_overwrite` inserts the same write record at two sequence numbers pointing to the same default-CF start timestamp, modeling overwrite visibility.
- `put_data_impl` performs the common encoded-key/value construction, memory-controller accounting, and skiplist insertion.
- `put_data_in_rocks` writes equivalent MVCC data into RocksDB for comparison tests.
- `new_region` builds a `kvproto::metapb::Region` with id, start/end keys, and one dummy peer.

## Control Flow

Skiplist helpers create a TiKV data key, append commit timestamp for write CF, encode it as an internal value key with a supplied sequence, attach the shared `MemoryController`, acquire estimated memory for the write-batch entry, and insert into the write handle. If `overwrite_seq_num` is supplied, the write CF entry is inserted again with a second sequence. For non-short values, the helper also writes the default-CF value at `start_ts` with sequence `seq_num + 1`. RocksDB helper writes the corresponding write CF entry and, unless the write type is delete or the value is short, writes default CF.

## State And Persistence Behavior

Skiplist helpers mutate in-memory CF handles and memory-controller counters. RocksDB helper persists to the provided temporary/test Rocks engine. The helpers do not clean up state themselves; tests own engine lifetimes.

## Dependencies And Integration Points

The file depends on `engine_traits::SyncMutable`, `engine_rocks::RocksEngine`, `txn_types::{Key, TimeStamp, Write, WriteType}`, local `keys::{data_key, encode_key, InternalBytes, ValueType}`, `MemoryController`, and `RegionCacheWriteBatchEntry` sizing. It is used by in-memory engine tests that need realistic MVCC write/default CF layouts.

## Risks And Edge Cases

`put_data_impl` uses `seq_num + 1` for default CF, so tests must choose sequence numbers intentionally when modeling snapshot visibility. Memory acquisition return values are ignored, which is acceptable for tests configured with adequate capacity but would hide limiter behavior in low-capacity scenarios. `put_data_in_rocks` uses `data_key(key)` for write CF but raw `key` for default CF, matching the expected test layout; callers must pass the right key shape. `new_region` adds a dummy peer solely to satisfy `CacheRegion::from_region` expectations.

## Test Signals

This is a support module rather than a test suite. Its signal is indirect through read, write-batch, and region-manager tests that use these helpers to construct MVCC fixtures.
