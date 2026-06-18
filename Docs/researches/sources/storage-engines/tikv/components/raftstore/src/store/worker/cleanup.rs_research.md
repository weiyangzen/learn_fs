# sources/storage-engines/tikv/components/raftstore/src/store/worker/cleanup.rs

## Purpose
This file is a small dispatcher that combines multiple cleanup-related raftstore workers behind one `Runnable`. It lets the store schedule compaction, imported SST deletion, and snapshot GC/delete tasks through a single cleanup worker interface.

## Important APIs, Types, and Functions
- `Task` wraps `CompactTask`, `CleanupSstTask`, and `GcSnapshotTask`.
- `Runner<E, R>` owns a `CompactRunner<E>`, `CleanupSstRunner<E>`, and `GcSnapshotRunner<E, R>`.
- `Runner::new` wires the three concrete runners.
- `impl Runnable for Runner` dispatches by enum variant.

## Control Flow
The worker receives a `Task`, formats it by delegating to the inner task's `Display`, and dispatches `Compact` to the compaction runner, `CleanupSst` to the SST importer cleanup runner, and `GcSnapshot` to the snapshot cleanup runner. There is no local retry or persistence logic in this wrapper.

## State and Persistence Behavior
This wrapper owns the concrete runners and mutably borrows them during dispatch. State and persistence effects are entirely delegated: RocksDB compaction in `compact`, importer filesystem deletion in `cleanup_sst`, and snapshot manager/router actions in `cleanup_snapshot`.

## Dependencies and Integration Points
It depends on `engine_traits::{KvEngine, RaftEngine}`, `tikv_util::worker::Runnable`, and sibling worker modules. It is an integration point for raftstore worker construction where separate cleanup responsibilities share a worker lane.

## Risks and Edge Cases
Because this is a serial dispatcher, long-running inner operations can block later cleanup tasks in the same worker. Error handling is delegated to inner runners, so wrapper-level observability only reflects task display strings.

## Test Signals
There are no direct tests in this file. Coverage comes indirectly from the concrete cleanup, compaction, snapshot, and SST worker tests and from raftstore worker integration tests that schedule `CleanupTask` variants.
