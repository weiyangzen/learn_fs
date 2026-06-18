# sources/storage-engines/foundationdb/fdbserver/workloads/MiniCycle.cpp

## Purpose
Transactional cycle-integrity workload. It partitions the keyspace into per-client mini-cycles, runs transactions that reverse links among three adjacent cycle nodes, and repeatedly verifies each cycle remains a single valid cycle.

## Important APIs, types, and functions
`MiniCycleWorkload` derives from `TestWorkload` and uses `bulkSetup`, key/value helpers with optional `keyPrefix`, `FlowLock` for serialized checks, retry counters, and latency metrics. Core methods are `cycleSize`, `beginKey`, `endKey`, `operator()` for initial links, `cycleClient`, `_check`, `_checkCycle`, `cycleCheckClient`, and `cycleCheckData`.

## Control flow
Setup bulk-loads the current client's mini-cycle. The start phase does nothing; check launches transaction clients for all client partitions for `testDuration` while periodically running full cycle checks. A cycle client picks a random node, reads three links, writes a reversal of the next links across those nodes, and commits with retry handling. Checkers read each partition range and walk values as pointers to ensure exactly one complete cycle with no missing, invalid, shorter, or longer loop.

## State and persistence behavior
State is normal key/value data where each key's value encodes the next node in the cycle. Transactions mutate three links atomically. No cleanup is performed.

## Dependencies and integration points
Uses bulk setup, normal transactions, optional span parent transaction option, deterministic key encoding, Flow locks, and tester metrics.

## Risks and test signals
Risks include the typo-like option name `"traceParentProbability "` with trailing space, check methods using `clientId` in places where `clientID` is passed, and high contention producing rate failures. Signals are cycle structural failures, bad reads, client/checker errors, minimum throughput checks, and retry/latency metrics.
