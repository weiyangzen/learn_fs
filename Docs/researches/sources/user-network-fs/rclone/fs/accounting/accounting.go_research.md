<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting.go -->
# sources/user-network-fs/rclone/fs/accounting/accounting.go

## Purpose

`accounting.go` implements the per-transfer accounting reader used to count bytes, enforce bandwidth and max-transfer limits, expose current progress, and wrap or unwrap stream chains.

## Important APIs, Types, and Functions

Key exports are `Start`, `Account`, `AccountSeeker`, `AccountReaderAt`, `AccountReadAtSeeker`, `Accounter`, `WrapFn`, `UnWrap`, and `UnWrapAccounting`. Error sentinels distinguish hard max-transfer limit failures from graceful no-retry stop conditions. `newAccountSizeName` constructs accounts for `Transfer`.

## Control Flow

`Start` initializes global token buckets, scheduled bandwidth updates, TPS limiting, and `fs.CountError`. An `Account` wraps an `io.ReadCloser`, optionally adds `asyncreader` buffering, records bytes on `Read`, `ReadAt`, `WriteTo`, explicit accounting, and server-side copy/move callbacks, then removes itself from in-progress state on `Done`.

## State and Persistence Behavior

State is in memory: per-account byte counters, moving average samples, current reader, async buffer, closed flag, exit channel, per-file limiter, and pointers into `StatsInfo`. The max-transfer limit reads global stats bytes, so per-account reads can be clipped to process/group state.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `Transfer`, global `TokenBucket`, per-file `BwLimitFile`, `asyncreader`, `fserrors`, remote-control stats, and transfer accounter callbacks for server-side operations.

## Risks and Test Signals

Risks include Read/Close races, goroutine leaks when `Done` is not called, accounting over/under-count around max-transfer clipping, async-buffer replacement bugs in `UpdateReader`, lock-order deadlocks, and Unicode shortening edge cases. Tests cover buffering, reader updates, max transfer, stream wrapping, seeker/reader-at wrappers, `WriteTo`, and name shortening; race tests are especially valuable.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/accounting.go -->
