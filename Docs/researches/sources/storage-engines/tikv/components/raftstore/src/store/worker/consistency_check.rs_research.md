# sources/storage-engines/tikv/components/raftstore/src/store/worker/consistency_check.rs

## Purpose
This worker computes region consistency hashes from engine snapshots and reports them back to the store/coprocessor dispatch path. It is used by raftstore consistency checking to compare replicated region data at a specific raft index.

## Important APIs, Types, and Functions
- `Task<S>::ComputeHash { index, context, region, snap }` carries the raft index, observer context, region metadata, and snapshot.
- `Task::compute_hash` is a constructor for compute-hash tasks.
- `Runner<EK, C>` owns a `StoreHandle` router and `CoprocessorHost<EK>`.
- `compute_hash` invokes coprocessor consistency-check observers and reports results.

## Control Flow
The runner receives `ComputeHash` and calls `compute_hash`. Empty context is skipped for backward compatibility. Otherwise it increments compute metrics, starts a hash timer, calls `coprocessor_host.on_compute_hash(&region, &context, snap)`, and handles errors by logging and incrementing failure metrics. Successful `(context, crc32)` results are encoded as big-endian four-byte checksums and sent to `router.update_compute_hash_result(region_id, index, ctx, checksum)`.

## State and Persistence Behavior
The worker reads from an engine snapshot and does not mutate engine state. It emits hash results through the store handle, which schedules result updates elsewhere. Metrics counters/histograms are updated in memory/exported Prometheus state.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, Snapshot}`, `kvproto::metapb::Region`, byteorder encoding, `CoprocessorHost`, `StoreHandle`, raftstore metrics, and worker metrics. Consistency-check observers registered in the coprocessor host provide the actual hash algorithms.

## Risks and Edge Cases
Empty context silently skips work, preserving compatibility but hiding malformed modern requests. Errors from coprocessor hashing stop all result reporting for the task. The checksum format is fixed at big-endian u32, so consumers must match that encoding.

## Test Signals
`test_consistency_check` registers a raw consistency-check observer, writes sample keys, computes the expected CRC including region state key, runs the task over a snapshot, and verifies that `SchedTask::UpdateComputeHashResult` carries the region ID, index, context, and encoded checksum.
