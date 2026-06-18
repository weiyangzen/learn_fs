<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_test.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_test.go

## Purpose

`stats_test.go` covers core `StatsInfo` helper math and lifecycle behavior.

## Important APIs, Types, and Functions

Tests target `eta`, `etaString`, `percent`, `StatsInfo.Error`, `_totalDuration`, `RemoteStats`, `timeRanges.merge`, `timeRanges.cull`, `timeRanges.total`, `PruneTransfers`, and `RemoveDoneTransfers`.

## Control Flow

The test file builds synthetic stats, transfers, and time ranges to verify edge cases such as invalid ETA inputs, overflow caps, overlapping transfer windows, retry-after/fatal/no-retry classification, and completed-transfer retention limits.

## State and Persistence Behavior

Tests are process-local but temporarily modify `MaxCompletedTransfers` and config values. Transfer/time-range state simulates active and completed operations without remote IO.

## Dependencies and Integration Points

It integrates with `fserrors`, `fs.ConfigInfo`, `Transfer`, and rc stats rendering.

## Risks and Test Signals

The tests protect user-visible stats formatting and accounting math. They should be extended when adding counters to `StatsInfo`, changing ETA semantics, or changing transfer retention behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_test.go -->
