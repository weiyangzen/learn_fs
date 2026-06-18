<!-- BEGIN_FILE_RESEARCH: sources/object-store/garage/src/util/background/worker.rs -->
# sources/object-store/garage/src/util/background/worker.rs

## Purpose
Core asynchronous worker scheduler for Garage background tasks, including lifecycle state transitions, backoff, status accounting, and graceful shutdown.

## Important APIs, types, and functions
Defines `WorkerState::{Busy, Throttled, Idle, Done}`, async trait `Worker` with `name`, `status`, `work`, and `wait_for_work`, `WorkerProcessor::run`, and private `WorkerHandler::step`. `EXIT_DEADLINE` bounds shutdown draining.

## Control flow
The processor accepts new boxed workers, assigns task ids, and drives each handler through a `FuturesUnordered` set. Busy workers call `work`; errors are logged, counted, timestamped, and converted to exponential `Throttled` sleeps. Idle workers wait for work or stop-signal changes; Done workers are removed. On shutdown, remaining workers are drained until deadline.

## State and persistence behavior
Worker state, error counters, consecutive error counts, and last errors are in memory and copied into the shared `WorkerInfo` map. There is no disk persistence, but errors influence runtime pacing through throttling.

## Dependencies and integration points
Uses Tokio select/watch/mpsc, `async_trait`, futures streams, Garage `Error`, `WorkerStatus`, and `now_msec`. All background subsystems implement this trait to participate in Garage process shutdown and status reporting.

## Risks and test signals
Risks include workers that never yield, unbounded repeated errors, and cancellation during long work after the exit deadline. The explicit `yield_now` for Busy loops is a fairness guard. Tests should simulate Busy/Idle/Done, error backoff, status map updates, and stop-signal deadline behavior.
<!-- END_FILE_RESEARCH: sources/object-store/garage/src/util/background/worker.rs -->
