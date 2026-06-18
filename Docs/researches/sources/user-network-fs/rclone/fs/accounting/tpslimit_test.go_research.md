<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go -->
# sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go

## Purpose

`tpslimit_test.go` checks that TPS limiting delays operations within expected timing bounds.

## Important APIs, Types, and Functions

`TestLimitTPS` uses an inner `timeTransactions` helper to call `LimitTPS` repeatedly and compare elapsed time to expected min/max windows.

## Control Flow

The test configures `tpsBucket` directly or via start logic, times transactions, and resets `tpsBucket` to nil afterward.

## State and Persistence Behavior

It mutates the package-global limiter and relies on wall-clock timing, making it sensitive to scheduler load.

## Dependencies and Integration Points

It integrates with the rate limiter and context handling.

## Risks and Test Signals

The test is a timing signal rather than a deterministic functional proof. CI slowness can cause flaky upper-bound failures; race tests should confirm no concurrent global-state surprises.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/tpslimit_test.go -->
