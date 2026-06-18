# sources/storage-engines/foundationdb/fdbserver/workloads/MaxGrvQueueDelay.cpp

## Purpose
End-to-end validation for the `MAX_GRV_QUEUE_DELAY` transaction option. It verifies that normal and permissive GRV requests succeed while a burst of zero-delay uncached GRV requests is rejected by proxy GRV queue throttling.

## Important APIs, types, and functions
`MaxGrvQueueDelayWorkload` exposes request counts, required rejection count, strict and permissive delay thresholds, warmup controls, start delay, timeout, completion/failure flags, and counters. It uses `FDBTransactionOptions::SKIP_GRV_CACHE`, `MAX_GRV_QUEUE_DELAY`, `errorOr`, `waitForAll`, and `transaction_grv_queue_rejected`.

## Control flow
Only client 0 runs in simulation when general buggify is disabled, and all failure injection is disabled. `run` waits `startAfter`, calls `verifyBaseline` with retries for a no-option request and a permissive option request, optionally launches warmup GRVs, then launches `requestCount` strict-option GRVs in parallel. It counts successes, expected rejections, and unexpected errors, then fails if fewer than `minRejected` requests were rejected.

## State and persistence behavior
The workload does not write keys. It only exercises transaction read-version requests with specific options and records in-memory counters.

## Dependencies and integration points
Depends on client transaction option encoding, proxy GRV queue ratekeeper configuration from test files, simulation environment, Flow buggify status, and error propagation.

## Risks and test signals
The workload is sensitive to external ratekeeper knob configuration and recovery backlog. Baseline retry reduces but does not eliminate startup flakiness. Signals are counters for requests/successes/rejected/unexpected errors, `MaxGrvQueueDelayTooFewRejections`, and completion/failure flags checked after timeout.
