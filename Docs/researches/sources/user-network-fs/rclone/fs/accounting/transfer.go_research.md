<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer.go -->
# sources/user-network-fs/rclone/fs/accounting/transfer.go

## Purpose

`transfer.go` models one logical transfer or check and connects object-level lifecycle events to `StatsInfo` and `Account`.

## Important APIs, Types, and Functions

`TransferSnapshot` is the JSON/rc view of a transfer. `Transfer` stores immutable identity fields plus mutable account, error, and completion time under a mutex. Constructors create check or transfer records, and methods include `Done`, `Reset`, `Account`, `TimeRange`, `IsDone`, `Snapshot`, and `rcStats`.

## Control Flow

Creating a transfer adds it to `StatsInfo.startedTransfers` and to checking/transferring maps via caller methods. `Account` creates or updates the accounting reader. `Done` records errors, closes and finalizes the account, marks completion, updates check/transfer counters, removes live maps, and prunes old completed transfers.

## State and Persistence Behavior

Transfer records remain in memory after completion until pruned. Snapshots include source/destination fs config strings when available. Errors are stored for completed-transfer reporting.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `Account`, `fs.DirEntry`, `fs.ObjectInfo`, remote-control output, and JSON marshaling.

## Risks and Test Signals

Risks include lock misuse in `Reset`, double `Done`, account close errors, retaining fs config strings, and completed-transfer pruning. Tests cover snapshot fields, done behavior, checking transfers, and rc stats.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer.go -->
