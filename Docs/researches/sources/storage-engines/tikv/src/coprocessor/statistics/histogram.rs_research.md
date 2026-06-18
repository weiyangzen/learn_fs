# sources/storage-engines/tikv/src/coprocessor/statistics/histogram.rs

## Purpose
Implements the coprocessor statistics histogram used for TiDB/TiKV analyze results. It incrementally receives already-sorted encoded datum bytes and builds a bounded bucket representation that can be serialized into `tipb::Histogram`.

## Important APIs, Types, and Functions
`Bucket` stores cumulative `count`, inclusive `lower_bound`/`upper_bound`, `repeats` for the upper bound, and optional per-bucket `ndv`. `Histogram` stores global `ndv`, `buckets`, `per_bucket_limit`, and `buckets_num`. `Histogram::new` starts with limit 1. `Histogram::append` is the public mutation path. `merge_buckets` halves bucket count by folding adjacent buckets and doubling `per_bucket_limit`. `From<Bucket>` and `From<Histogram>` convert internal state to protobuf `tipb` structures.

## Control Flow
`append` assumes each new item is greater than or equal to the current maximum. If it equals the last bucket upper bound, it only increments the current bucket count and repeat count, preserving the invariant that one value does not span buckets. New distinct values increment global `ndv`. If the bucket vector is at capacity and the last bucket is full, neighboring buckets are merged before insertion. The value is appended to the last bucket if it still has capacity; otherwise a new bucket is created with cumulative count inherited from the previous bucket.

## State and Persistence Behavior
All state is in memory until converted to `tipb::Histogram`. Bucket counts are cumulative rather than per-bucket, so readers must subtract previous bucket counts to recover bucket-local counts. `with_bucket_ndv` controls whether bucket `ndv` is maintained; global `ndv` is always updated for distinct append values.

## Dependencies and Integration Points
Depends on `tipb::{Histogram,Bucket}` for output and TiDB datum encoding in tests. This is part of `coprocessor::statistics` and is consumed by analyze/statistics code that must feed sorted encoded values.

## Risks and Edge Cases
The sorted-input contract is critical and not enforced. Supplying out-of-order bytes corrupts bounds and NDV semantics. `buckets_num == 0` would make `append` try to unwrap an empty last bucket after merge/capacity checks, so callers should avoid zero bucket counts. Merge logic uses cumulative-count rewrites and `mem::swap`, making off-by-one or odd bucket-count regressions high risk.

## Test Signals
`test_histogram` covers bucket creation, merges, repeated values, NDV, and per-bucket limits. `test_buckets_limit` covers single-bucket merge behavior. Tests exercise encoded TiDB `Datum::I64` values but do not cover zero bucket count or unsorted input.
