# sources/storage-engines/tikv/tests/failpoints/cases/test_stats.rs

## Purpose
This small failpoint test validates region bucket statistics reporting for read and write traffic. It confirms bucket metadata and per-bucket read/write counters are collected and reported to PD when region buckets are enabled.

## Important APIs, Types, And Functions
The test uses `must_new_and_configure_cluster_and_kv_client` to build a cluster and raw KV client while enabling `coprocessor.enable_region_bucket`, setting long split-check interval, short `report_region_buckets_tick_interval`, and disabling hibernate regions. It issues writes through `cluster.must_put`, point reads through `cluster.must_get`, and a `RawBatchGetRequest` through the KV client. `cluster.must_get_buckets(1)` retrieves reported bucket data. The failpoint `mock_tick_interval` forces tick scheduling to return immediately.

## Control Flow
After cluster startup and failpoint installation, the test writes 50 keys shaped as `[b'k', i]` with 4-byte values, reads them individually, then sends one raw batch-get over the same key set. It waits for bucket reporting, fetches buckets for region 1, and asserts bucket metadata contains the expected two boundary keys and one stats bucket.

## State And Persistence Behavior
Persistent state is the 50 raw KV entries. Transient/statistical state is bucket metadata and bucket read/write counters accumulated by raftstore/coprocessor reporting. Hibernate is disabled to keep the region active long enough for bucket stats to be reported.

## Dependencies And Integration Points
The test integrates raw KV RPCs, raftstore bucket reporting, PD test-client bucket retrieval, coprocessor bucket configuration, and failpoint-controlled tick intervals.

## Risks And Edge Cases
Risks include bucket reports being skipped while a region hibernates, read/write byte accounting excluding key bytes or value bytes incorrectly, batch reads not contributing to read stats, and bucket metadata not being initialized when split checks are effectively disabled.

## Test Signals
Expected signals are `buckets.meta.keys.len() == 2`, `write_keys == [50]`, `write_bytes == [50 * (4 + 2)]`, `read_keys == [50]`, and `read_bytes == [50 * (4 + 2)]`.
