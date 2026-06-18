# sources/storage-engines/foundationdb/fdbserver/workloads/Cycle.cpp

Purpose: Implements `Cycle`, a transactional integrity workload that maintains a single directed cycle over `nodeCount` keys while concurrent clients repeatedly reverse three links. It is a broad read/write conflict, clear-range, tracing, and final data-shape check.

Important APIs/types/functions: `CycleWorkload`, `bulkSetup`, `cycleClient`, `cycleCheck`, `cycleCheckData`, `key`, `value`, `keyRange`, `badRead`, `PerfIntCounter`, `PerfDoubleCounter`, `Span`, `FDBTransactionOptions::SPAN_PARENT`, and simulator speed-up hooks.

Control flow: Setup optionally disables unseed checking and bulk-loads keys unless `skipSetup`. `start` launches `actorCount` timed `cycleClient` actors. Each client picks a random node, reads the next three links, clears a range around `r`, writes a reversed local segment, commits with retry accounting, and records latency. `check` detects client errors and client 0 scans the whole key range to verify the cycle length and key order.

State and persistence behavior: Persistent state is the cycle encoded as key/value pairs under `keyPrefix`, where values point to the next node. Runtime state is counters and client futures. The workload intentionally uses clear-range plus point writes to exercise mutation ordering and storage-engine point-delete conversion.

Dependencies/integration: It uses `BulkSetup.h`, Native API transactions, deterministic randomness, Flow tracing, simulator knobs for read-window recovery, and tester performance metrics.

Risks: Final validation requires reading `nodeCount + 1` keys and can suffer `transaction_too_old`; after many retries simulation is sped up. Missing values are traced but dereferenced, so true corruption can crash fast. Metrics divide by transaction count, which assumes at least one successful transaction.

Test signals: `TestFailure` reasons for node count, key changes, invalid values, shorter/longer cycles; retry counters by error type; approximate read/write rows per simulated second; and no client future errors.
