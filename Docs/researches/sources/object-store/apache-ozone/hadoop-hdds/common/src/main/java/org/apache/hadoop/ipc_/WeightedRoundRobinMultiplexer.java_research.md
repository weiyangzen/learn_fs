# sources/object-store/apache-ozone/hadoop-hdds/common/src/main/java/org/apache/hadoop/ipc_/WeightedRoundRobinMultiplexer.java

## Purpose
`WeightedRoundRobinMultiplexer` chooses which priority queue a call consumer should inspect next. It gives higher priority queues more service opportunities while periodically serving lower priority queues to reduce starvation.

## Important APIs, types, and functions
- Config key `faircallqueue.multiplexer.weights`, namespaced by the caller, supplies one integer weight per queue.
- Constructor validates positive queue count, loads weights, applies defaults when absent, validates exact weight count, and initializes `currentQueueIndex` and `requestsLeft`.
- `getDefaultQueueWeights(int)` returns descending powers of two by priority, so queue 0 receives the largest default share.
- `getAndAdvanceCurrentIndex()` returns the current queue index and decrements remaining requests for the current queue.

## Control flow
On each call, the current index is read, then `advanceIndex` decrements `requestsLeft`. When the decrement result equals zero, `moveToNextQueue` advances `currentQueueIndex` modulo `numQueues` and resets `requestsLeft` to the next queue's configured weight. The design accepts extra reads from a queue under races because atomic operations avoid coarse locking.

## State and persistence behavior
Runtime state is in-memory: `numQueues`, `queueWeights`, `currentQueueIndex`, and `requestsLeft`. No data is persisted.

## Dependencies and integration points
It implements `RpcMultiplexer` and is used by fair-call-queue style IPC call queues. It reads weights from Hadoop `Configuration` using the queue namespace.

## Risks and edge cases
The constructor rejects zero or negative queue counts and mismatched custom weight lengths, but it does not explicitly reject zero or negative weight values. A zero weight can drive immediate or odd advancement behavior; negative values can prevent normal equality-to-zero advancement. Concurrent callers can observe more reads than the nominal weighted cycle by design.

## Test signals
Tests should cover default weights for 1, 2, and N queues; exact custom weights; mismatched custom weight length; invalid queue count; concurrent `getAndAdvanceCurrentIndex`; and behavior under zero or negative configured weights if the surrounding system permits such config.
