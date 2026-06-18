# sources/storage-engines/foundationdb/flow/include/flow/TxnCounters.h

## Purpose
Defines a small bundle of transaction lifecycle counters for started, committed, and aborted transactions.

## Important APIs, Types, And Functions
`TxnCounters` contains three `SimpleCounter<int64_t>*` fields. `makeCounters(const char* prefix)` allocates the bundle and creates counters named `<prefix>/started`, `<prefix>/committed`, and `<prefix>/aborted`.

## Control Flow
The caller requests counters by prefix and then increments the returned counters elsewhere. This header performs construction only.

## State And Persistence Behavior
Counters are process-local metrics, not durable database state. `makeCounters` returns raw heap allocations, implying process/global lifetime ownership.

## Dependencies And Integration Points
Depends on `flow/SimpleCounter.h`. Integrates with components that want consistent transaction lifecycle metric names.

## Risks And Edge Cases
Repeated dynamic creation can leak counters. Prefix reuse can collide metric names or merge unrelated measurements.

## Test Signals
Verify counter names and indirect increments from transaction lifecycle paths.
