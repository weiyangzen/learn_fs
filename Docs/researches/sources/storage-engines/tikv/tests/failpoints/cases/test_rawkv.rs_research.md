# sources/storage-engines/tikv/tests/failpoints/cases/test_rawkv.rs

## Purpose
This file tests RawKV API v2 behavior with causal timestamps during leader transfer, region merge, and in-flight raw put key guards.

## Important APIs, Types, and Functions
- `TestSuite` wraps a `ServerCluster`, API version, context/client construction, raw put/get helpers, timestamp flushing, causal timestamp provider access, region merge, and leader-transfer checks.
- `FP_GET_TSO` (`test_raftstore_get_tso`) mocks TSO fetches to simulate stores with stale timestamp batches.
- Tests are `test_leader_transfer`, `test_region_merge`, and `test_raw_put_key_guard`.

## Control Flow
The leader-transfer test writes on store 1, flushes its timestamp, forces TSO fetch to return an older timestamp, transfers leadership to store 2, and expects raw puts to fail with `max_timestamp_not_synced` until timestamp sync succeeds. The merge test splits into three adjacent regions with leaders on different stores, writes/flushes on one source region, forces stale TSO during merge into another leader, verifies raw puts are rejected, then allows TSO and merges again with successful writes. The key-guard test pauses raw async write, waits for `global_min_lock_ts`, verifies it matches the raw put guard timestamp and that the key is invisible, then resumes and checks guard cleanup.

## State and Persistence Behavior
The suite tracks API v2 raw key/value state, causal timestamp provider batches, concurrency manager `global_min_lock_ts`, and merged-region boundaries. Raw writes must not persist when max timestamp is not synchronized; key guards must exist only while the write is in progress.

## Dependencies and Integration Points
It integrates causal timestamp providers, PD TSO, raw KV gRPC requests, region split/merge, leader transfer, concurrency manager lock state, and API-version-aware request contexts.

## Risks and Test Signals
Risks include accepting raw writes with stale timestamp after leader transfer or merge, corrupting causal ordering, or leaking key guards after raw writes. Signals are `max_timestamp_not_synced` region errors, stable raw-get values before allowed writes, merged range boundary assertions, and `global_min_lock_ts` equality/absence.
