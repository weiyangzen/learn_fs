# sources/storage-engines/tikv/components/raftstore/src/coprocessor/split_check/half.rs

## Purpose
`half.rs` implements load/admin half-split behavior: while scanning it records bucket boundary keys and returns a middle key, and in approximate mode it asks the engine for one approximate middle split key.

## Important APIs, Types, And Functions
`Checker` stores scanned bucket starts, current bucket size, target bucket size, and policy. `HalfCheckObserver` installs the checker for non-size split reasons. `half_split_bucket_size` derives a bucket target from region max size with a 1024-bucket cap and a 512 MiB per-bucket ceiling. `get_region_approximate_middle` calls `KvEngine::get_range_approximate_split_keys(range, 1)`.

## Control Flow
`on_kv` pushes the first key and every key after the current bucket reaches `each_bucket_size`, then accumulates entry size. `split_keys` returns the middle bucket key converted from data key to origin key, or no key if fewer than two buckets were recorded. `approximate_split_keys` returns at most one key from engine range properties.

`HalfCheckObserver::add_checker` skips `SplitReason::Size` so size-based split checks rely on size/keys checkers. For load/admin reasons it adds the half checker with the requested policy.

## State And Persistence Behavior
State is per split-check run only. The checker keeps bucket keys in memory and does not update raftstore directly. Actual split requests are issued later by the split-check runner through the host and `StoreHandle`.

## Dependencies And Integration Points
Uses `engine_traits::{KvEngine, Range}`, `kvproto` split reason/policy, TiKV `ReadableSize`, and shared split-check host traits. It is registered by default in `CoprocessorHost::new` with priority 100.

## Risks
Approximate middle depends on range properties and can be unavailable or imprecise for small/unflushed data. Scan mode memory grows with the number of bucket boundaries, bounded by bucket sizing rather than a hard vector length. The returned key is a bucket start near the middle, not necessarily a byte-perfect median.

## Test Signals
Tests verify checker selection by split reason, load split midpoint behavior, scan and approximate midpoint output, split checks over explicit key ranges, bucket generation for normal/MVCC/deleted-data cases, and approximate middle across column families.
