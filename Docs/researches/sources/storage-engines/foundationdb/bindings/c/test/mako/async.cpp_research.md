# sources/storage-engines/foundationdb/bindings/c/test/mako/async.cpp

## Purpose
Implements callback-driven resumable state machines for Mako population and workload execution without coroutines.

## Important APIs, types, and functions
`ResumableStateForPopulate::runOneTick` inserts generated rows and commits in batches. `ResumableStateForRunWorkload::runOneTick` drives operation steps from `opTable`, handles immediate versus future steps, and records stats. `onTransactionSuccess`, `onIterationEnd`, `updateStepStats`, `updateErrorStats`, and `isExpectedError` manage lifecycle and error classification.

## Control flow
State machines repost themselves to Boost.Asio and capture `shared_from_this` in FDB callbacks. Immediate client-side steps loop locally; future-returning steps register continuations and resume later.

## State and persistence behavior
Population writes generated records; workloads mutate data according to operation mix. In-memory state includes transactions, buffers, iterators, stopwatches, counters, and stop signals.

## Dependencies and integration points
Depends on Mako operations, stats, time, utils, logger, `future.hpp`, Boost.Asio, and `fdb_api.hpp`.

## Risks and test signals
Callback lifetime, transaction reset boundaries, retry loops, timeout classification, and stats skew are risks. Signals are operation/error/conflict/timeout counts and latency outputs.
