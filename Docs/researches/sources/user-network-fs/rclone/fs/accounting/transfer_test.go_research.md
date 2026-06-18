<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer_test.go -->
# sources/user-network-fs/rclone/fs/accounting/transfer_test.go

## Purpose

`transfer_test.go` validates `Transfer` lifecycle and snapshot/rc output.

## Important APIs, Types, and Functions

`TestTransfer` creates a transfer with a mock object, checks snapshots before and after completion, verifies rc stats, and covers checking-transfer snapshots.

## Control Flow

The test constructs `StatsInfo`, mock source/destination fs values, calls `newTransfer`, inspects `Snapshot`, calls `Done`, and validates completion timestamps and fields.

## State and Persistence Behavior

All state is in memory. The test exercises stats counters and transfer retention indirectly.

## Dependencies and Integration Points

It integrates with `mockobject`, fs config strings, and `StatsInfo`.

## Risks and Test Signals

It signals stable JSON/rc-visible transfer fields. Additional coverage would be useful for `Account`, `Reset`, error snapshots, and double completion.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfer_test.go -->
