<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go -->
# sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go

## Purpose

`token_bucket_test.go` validates the remote-control interface for bandwidth limits.

## Important APIs, Types, and Functions

`TestRcBwLimit` retrieves the `core/bwlimit` rc call and tests setting/querying rates such as `1M`, `off`, and asymmetric pairs.

## Control Flow

The test calls the rc handler with different `rc.Params`, checks returned `rate`, `bytesPerSecond`, `bytesPerSecondTx`, and `bytesPerSecondRx`, and verifies state persists for subsequent query calls.

## State and Persistence Behavior

It mutates the global `TokenBucket` state in process. Tests that run afterward can observe the last configured limit unless they reset it.

## Dependencies and Integration Points

It integrates with rc call registration, `fs.BwTimetable` parsing, and token bucket state.

## Risks and Test Signals

The test protects rc API shape but does not measure real throttling, scheduled timetables, or signal toggling. Additional tests should reset global state and cover invalid rates.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket_test.go -->
