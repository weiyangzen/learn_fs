# sources/storage-engines/foundationdb/fdbserver/workloads/Watches.cpp

## Purpose
`WatchesWorkload` builds a chain of watch-driven key propagation. Watcher actors copy values from one key to the next when watches fire, while a worker changes the first key and waits for the expected value to reach the final key.

## Important APIs, Types, and Functions
The workload uses `Transaction::watch()`, `Watch`, `cx.run()`, `DDSketch`, `DeterministicRandom`, `CODE_PROBE`, and `PerfIntCounter`. Helpers are `keyForIndex()`, `watcherInit()`, static `watcher()`, and `watchesWorker()`.

## Control Flow
`setup()` distributes nodes across clients, writes extra keys for each watch key, and launches watcher actors. Client 0 `start()` runs `watchesWorker()`. Each watcher reads its watch and set keys; if values differ, it writes the watched value to the set key, otherwise it registers a watch and waits for it. The worker toggles or clears the start key, then repeatedly reads the end key or watches it until the expected value appears. Each completed propagation increments `cycles` and records per-node cycle latency.

## State and Persistence Behavior
Database state includes generated chain keys plus many extra keys per node initialized with 100-byte values. Runtime state includes background watcher futures in `clients`, deterministic node order, cycle count, and latency sketch. The workload does not clean up keys.

## Dependencies and Integration Points
It integrates with Native API watches, transaction retry helper `cx.run()`, Flow code probes, DDSketch metrics, and tester failure-injection controls. It disables `RandomRangeLock` because watcher transactions do not handle range-lock rejection errors.

## Risks and Edge Cases
Watcher actors run forever and are cleared only in `check()`. `watcher()` reports `WatcherTriggeredWithoutChanging` if a watch fires without observed value change. The chain relies on all watcher actors staying healthy; `check()` inspects stored futures for errors. Heavy `extraPerNode` setup can create substantial database load.

## Test Signals
Metrics on client 0 include cycles and mean latency per node. Error traces include `WatcherTriggeredWithoutChanging` and `WatcherError`. `check()` returns false if any watcher future is in error.
