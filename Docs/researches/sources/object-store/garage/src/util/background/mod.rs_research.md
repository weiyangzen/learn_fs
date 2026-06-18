<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/mod.rs -->
# sources/object-store/garage/src/util/background/mod.rs

## Purpose
Public entry point for Garage background work scheduling. It wires worker registration, status collection, and the worker processor loop.

## Important APIs, types, and functions
Exports `vars`, `worker`, `Worker`, and `WorkerState`. Defines `BackgroundRunner`, `WorkerInfo`, and `WorkerStatus`; important methods are `BackgroundRunner::new`, `get_worker_info`, and `spawn_worker`.

## Control flow
`new` creates an unbounded worker channel and shared status map, starts `WorkerProcessor::run` as a Tokio task, and returns both runner and join handle. `spawn_worker` boxes any `Worker` and sends it to the processor; status snapshots clone the mutex-protected map.

## State and persistence behavior
State is in-memory process state: queued workers, task ids, latest status, error counts, and last error timestamps. Persistent knobs may be exposed through `background/vars.rs`, but this module itself does not write disk state.

## Dependencies and integration points
Used by table Merkle/sync/GC workers, insert queues, and other long-running Garage services. Integrates Tokio channels/watch signals and worker traits from `worker.rs`.

## Risks and test signals
The unbounded channel assumes worker creation is controlled; abuse could grow memory. Status locking should remain short. Tests or runtime signals include worker info visibility, graceful shutdown through the watch signal, and no panic when workers exit.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/mod.rs -->
