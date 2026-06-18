# sources/storage-engines/foundationdb/bindings/c/test/mako/async.hpp

## Purpose
Declares heap-resident resumable Mako execution state for asynchronous population and workloads.

## Important APIs, types, and functions
`ResumableStateForPopulate` stores logger, database/transaction, `io_context`, arguments, stats, stop counter, key range/checkpoint, buffers, and stopwatches. `ResumableStateForRunWorkload` stores operation iterator, buffers, transaction state, counters, stop signal, and latency watches.

## Control flow
Both structs inherit `enable_shared_from_this`, expose `runOneTick`/`postNextTick`, and signal completion by incrementing a shared stop counter.

## State and persistence behavior
They own transient benchmark execution state. FDB persistence is caused by transaction operations in the implementation.

## Dependencies and integration points
Depends on Boost.Asio, Mako `Arguments`, `WorkflowStatistics`, shared-memory signals, `future.hpp`, logger, and time helpers.

## Risks and test signals
Fields must be reset at transaction/iteration boundaries. Stop counters and signal values are the orchestration signals.
