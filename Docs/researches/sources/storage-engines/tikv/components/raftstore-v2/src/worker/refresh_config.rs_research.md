# sources/storage-engines/tikv/components/raftstore-v2/src/worker/refresh_config.rs

## Purpose
This file provides the raftstore-v2 worker that applies online refresh-config tasks affecting runtime pools: raft batch-system poller threads, apply future-pool threads, and store writer threads. It converts `RefreshConfigTask` messages into bounded resizing operations without restarting the store.

## Important APIs, Types, and Functions
- `PoolController<N, C, H>` wraps a `BatchRouter` and `PoolState` for a batch-system pool. It owns the low-level increase/decrease operations for raft poller workers.
- `PoolController::decrease_by()` sends `FsmTypes::Empty` sentinel messages into the FSM sender, causing pollers to exit.
- `PoolController::increase_by()` builds new normal-priority handlers, creates `Poller` instances, preserves current thread-group properties, sets IO type to `ForegroundWrite`, and spawns named worker threads with `spawn_wrapper`.
- `Runner<EK, ER, H, T>` holds the logger, raft pool controller, `WriterContoller`, and apply `FuturePool`.
- `resize_raft_pool()`, `resize_apply_pool()`, and `resize_store_writers()` implement the three supported scaling surfaces.
- The `Runnable` implementation handles `RefreshConfigTask::ScalePool(BatchComponent::Store|Apply, size)` and `RefreshConfigTask::ScaleWriters(size)`, logging unsupported tasks.

## Control Flow
The worker receives a `RefreshConfigTask` from the background worker scheduler. Store-pool changes compare requested size with `expected_pool_size`, update the expectation, and either inject empty FSMs to shrink or spawn new pollers to grow. Apply-pool changes call `FuturePool::scale_pool_size()` and log when the requested size is clamped by configured thread-count limits. Store-writer changes update the expected writer size, then call `decrease_to` or `increase_to` on the underlying writer pool using cloned writer metadata.

## State and Persistence Behavior
This code changes only live process state. It mutates `PoolState.expected_pool_size`, `PoolState.id_base`, the `workers` vector, apply-pool runtime size, and writer-controller expected writer count. It does not persist configuration values; persistence and config distribution are upstream online-config concerns.

## Dependencies and Integration Points
It is built around `batch_system::{BatchRouter, PoolState, Poller, HandlerBuilder}`, `raftstore::store::{RefreshConfigTask, BatchComponent, WriterContoller}`, `StoreRouter`, and the raftstore-v2 `PeerFsm`/`StoreFsm` FSM types. It uses TiKV thread wrappers, thread names, IO type tagging, and `FuturePool` for apply scaling.

## Risks and Edge Cases
- Shrink requests rely on empty FSM sentinel delivery; a saturated or closed FSM channel logs an error and can leave the actual pool larger than expected.
- `increase_by()` unwraps thread spawning, so thread creation failure will panic.
- Apply-pool scaling may be clamped, but the method only logs the clamp and does not update the requested configuration.
- Store writer resizing relies on pollers refreshing cached writer handles later in `poller.begin()`, so there can be a temporary mismatch between expected and local cached writers.

## Test Signals
No direct tests are in this file. Integration coverage is indirect through raftstore-v2 tests that start systems, dispatch writes/admin commands, and rely on working raft/apply/store writer pools. The explicit warning logs for unsupported tasks are a signal that tests should assert only supported `RefreshConfigTask` variants if this worker is isolated later.
