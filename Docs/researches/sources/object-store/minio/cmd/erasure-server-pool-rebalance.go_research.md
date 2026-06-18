# sources/object-store/minio/cmd/erasure-server-pool-rebalance.go

## Purpose
This file implements pool rebalance, which moves data out of pools that have less free-space ratio than the deployment-wide goal. It owns `rebalance.bin` state, per-pool stats, start/stop/resume behavior, bucket/object migration, final status updates, audit logging, and trace metrics.

## Important APIs, Types, and Functions
`rebalanceStats` stores initial free/capacity, bucket queues, completed buckets, last bucket/object, object/version/byte counters, a participation flag, and `rebalanceInfo`. `rebalanceInfo` records start/end time and `rebalStatus`; statuses are `rebalNone`, `rebalStarted`, `rebalCompleted`, `rebalStopped`, and `rebalFailed`. `rebalanceMeta` stores global stopped time, operation ID, target free-space ratio, and per-pool `rebalanceStats`.

Key methods include `loadRebalanceMeta`, `updateRebalanceStats`, `initRebalanceMeta`, `nextRebalBucket`, `bucketRebalanceDone`, `rebalanceMeta.load/save`, `IsRebalanceStarted`, `IsPoolRebalancing`, `rebalanceBuckets`, `checkIfRebalanceDone`, `listObjectsToRebalance`, `rebalanceBucket`, `saveRebalanceStats`, `rebalanceObject`, `StartRebalance`, and `StopRebalance`.

## Control Flow
`initRebalanceMeta` computes total capacity and free space from `StorageInfo`, stores `PercentFreeGoal`, initializes each pool's stats and bucket queue, and marks pools with below-goal free-space ratio as participating and started.

`StartRebalance` exits if no metadata exists or if the operation was stopped. Otherwise it creates a cancelable global context, records the cancel function, snapshots participating started pools, and launches `rebalanceBuckets` only on the leader node for each pool.

`rebalanceBuckets` runs a periodic saver goroutine that writes stats every randomized 5 to 10 seconds and writes terminal status when the worker exits. The main loop fetches the next bucket and calls `rebalanceBucket`.

`rebalanceBucket` loads versioning, lifecycle, object lock, and replication config, then starts bounded workers per erasure set. It lists raw object metadata, sorts versions oldest first, skips remote tiered versions, applies lifecycle expiry, copies delete markers with `DeleteObject`, copies data versions via `rebalanceObject`, updates stats, and deletes source object versions when all versions are rebalanced.

## State and Persistence Behavior
`rebalance.bin` has a 4 byte little-endian format/version header and msgp-encoded `rebalanceMeta`. It is read and written through the first server pool. `saveRebalanceStats` loads the current persisted state under lock before merging local per-pool stats or stopped time, which reduces overwrite risk between nodes.

`StoppedAt` is global operation state; if set, `IsRebalanceStarted` and `IsPoolRebalancing` return false. Per-pool terminal status is stored in each `rebalanceStats.Info`.

## Dependencies, Risks, and Test Signals
The file depends on lifecycle, object lock, replication, versioning, hash readers, audit logging, trace subscriptions, worker pools, raw metadata listing, shortuuid IDs, peer notification reloads, and the core object APIs in `erasure-server-pool.go`.

`findIndex` works for append-style expansion but does not compare durable pool identity. Remote/tiered versions are skipped. `checkIfRebalanceDone` estimates free-space progress from bytes moved, which may diverge from actual disk state under concurrent writes or parity effects. Generated codec tests cover zero-value serialization, but there is no direct handwritten unit test for rebalance planning, migration, stop/resume, or save merging in this work item.
