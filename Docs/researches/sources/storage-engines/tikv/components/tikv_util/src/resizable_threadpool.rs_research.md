# sources/storage-engines/tikv/components/tikv_util/src/resizable_threadpool.rs

## Purpose
Implements a resizable Tokio runtime wrapper by replacing the entire runtime and draining old tracked tasks on a keeper runtime.

## Important APIs, Types, and Functions
- `DeamonRuntime` wraps `Option<Runtime>` plus `TaskTracker` and shuts down the runtime in `Drop`.
- `DeamonRuntimeHandle` is a weak handle that can `spawn` or `block_on` tracked tasks if the runtime is still alive.
- `ResizableRuntime` stores current size/version, thread prefix, keeper runtime, current runtime, construction callback, and post-adjust callback.
- `adjust_with(new_size)` creates a new runtime, swaps it in, and schedules old-runtime drain/drop.

## Control Flow
Construction creates a one-thread keeper runtime and the initial worker runtime. Spawns and block-ons go through a handle that briefly locks the current runtime to clone the Tokio handle and task tracker, then schedules the tracked future. Resizing increments a versioned thread-name suffix, builds a replacement runtime, swaps it under lock, updates size, and uses the keeper runtime to close and wait for the old tracker before dropping the old runtime.

## State and Persistence Behavior
Runtime state is process-local. Old runtimes remain alive until all tracked tasks complete; pending forever tasks prevent cleanup of that old runtime. Dropping `ResizableRuntime` drops current and keeper runtimes, and weak handles after drop log and ignore tasks.

## Dependencies and Integration Points
Depends on `tokio`, `tokio_util::task::TaskTracker`, `futures::Future`, and `crate::thread_name_prefix::RUNTIME_KEEPER_THREAD`. Callers supply the runtime-building policy and resize side-effect callback.

## Risks
The type name consistently uses `Deamon` rather than `Daemon`, which is cosmetic but public. Infinite or stuck tasks keep old runtimes alive after resize. `block_on` through stale handles may run on the runtime current at call time, not necessarily the runtime current when the handle was created.

## Test Signals
Tests cover resizing and cleanup after finite tasks, old-runtime retention for pending tasks, drop behavior with pending spawned/blocking tasks, and many concurrent handle operations.
