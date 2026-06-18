<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats.go -->
# sources/user-network-fs/rclone/fs/accounting/stats.go

## Purpose

`stats.go` is the central accounting state machine for rclone operations. It tracks bytes, checks, transfers, deletes, renames, listings, errors, retry/fatal flags, queues, elapsed transfer time, current/completed transfer records, and server-side copy/move counters.

## Important APIs, Types, and Functions

`StatsInfo` is the main type. Important APIs include `NewStats`, `RemoteStats`, `String`, `Log`, byte/error counters, `DeleteFile`, reset methods, transfer lifecycle methods, queue setters, transfer pruning, and server-side counters. Helper types/functions include moving-average state, `timeRange`, `eta`, `etaString`, `percent`, and `transferStats`.

## Control Flow

Transfers/checks are added through `NewTransfer` or `NewCheckingTransfer`, update byte counters through `Account`, and finish through `DoneTransferring`/`DoneChecking`. `calculateTransferStats` combines queue, completed, and in-progress data. The average loop starts when transfers begin and stops when no transfer/check remains. `String` and `RemoteStats` render consistent human/rc views.

## State and Persistence Behavior

All state is in memory and protected by `StatsInfo.mu`, nested average mutexes, and transfer maps. Completed transfers are retained up to `maxCompletedTransfers`; old time ranges are merged/cull-pruned to keep duration accounting bounded. Reset methods clear counters and carefully stop/restart the average goroutine only when needed.

## Dependencies and Integration Points

It integrates with `fs.ConfigInfo`, `fserrors`, `rc.Params`, terminal title updates, `Transfer`, `transferMap`, `inProgress`, stats groups, Prometheus, and `fs.CountError`.

## Risks and Test Signals

Risks include lock-order deadlocks with transfer maps, goroutine leaks after reset, inaccurate ETA/duration for overlapping transfers, stale last errors, max-delete threshold off-by-one errors, and retention pruning mistakes. Tests cover ETA, percent, error classification, duration merging/culling, remote stats, and pruning; race testing is important.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats.go -->
