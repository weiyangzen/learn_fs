# sources/storage-engines/foundationdb/fdbserver/workloads/WriteTagThrottling.cpp

## Purpose
`WriteTagThrottling.cpp` implements the `WriteTagThrottling` workload, which validates tag-based write throttling by comparing "bad" actors that concentrate writes and clears on hot ranges against "good" actors that use random keys.

## Important APIs, Types, and Functions
The main type is `WriteTagThrottlingWorkload : KVWorkload`, registered as `WriteTagThrottling`. Configuration includes actor counts, reads/writes/clears per transaction, `badOpRate`, `hotRangeRate`, `writeThrottle`, `populateData`, `keyCount`, and transaction pacing. `clientActor` runs the read/write workload. `throttledTagUpdater` polls `ThrottleApi::getThrottledTags`, and `recordThrottledTags` accumulates observed throttled tags. `generateKey`, `generateRange`, and `generateVal` produce transaction data.

## Control Flow
`setup` first checks transaction tag knob capacity and can fast-succeed when tags are unsupported. `_setup` optionally bulk-loads data and enables automatic throttling on client 0. `_start` launches good and bad actors plus a tag polling actor and runs them until `testDuration`. Each client actor paces transactions with `poisson`, tags transactions when `writeThrottle` is enabled, runs clear, set, and get operations, commits, records latency, and retries with `tr.onError`.

## State and Persistence Behavior
The workload persists only generated KV data and transaction mutations. Runtime metrics are in member counters and `DDSketch` latency samplers. Bad actors target deterministic per-actor hot ranges derived from client and actor id, making throttling attribution stable across the run.

## Dependencies and Integration Points
It integrates with tester `KVWorkload`, `BulkSetup`, FDB `Transaction`, `TransactionTag`, `FDBTransactionOptions::AUTO_THROTTLE_TAG`, and `ThrottleApi`. It depends on client knobs `MAX_TAGS_PER_TRANSACTION` and `MAX_TRANSACTION_TAG_LENGTH`.

## Risks and Edge Cases
The `check` method is intentionally more diagnostic than strict. If no throttling occurs it logs a warning, and it fails only when observed throttled tags exclude the bad tag. Average latency metrics divide by transaction counts, so configurations that produce zero transactions can make metric output fragile. Hot-range sizing also depends on `badActorPerClient`; zero bad actors skips range division but removes the intended bad-client signal.

## Test Signals
Metrics include bad/good transaction counts, retries, throttle retries, too-old and commit-failed retries, and latency summaries. Warnings `NoThrottleTriggered` and `IncorrectThrottle` signal likely configuration or behavior issues.
