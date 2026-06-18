<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket.go -->
# sources/user-network-fs/rclone/fs/accounting/token_bucket.go

## Purpose

`token_bucket.go` implements global bandwidth limiting for rclone accounting and transport paths.

## Important APIs, Types, and Functions

Exports include global `TokenBucket`, `TokenBucketSlot`, and slot constants for accounting, transport RX, and transport TX. Internal `buckets` and `tokenBucket` hold current/previous limiters and schedule state. Key methods are `StartTokenBucket`, `StartTokenTicker`, `LimitBandwidth`, `SetBwLimit`, and rc handler `rcBwlimit`.

## Control Flow

Startup reads `ConfigInfo.BwLimit`, creates `rate.Limiter` buckets when limits are set, empties initial bursts, starts optional signal handling, and may start a minute ticker for scheduled limit changes. Read/accounting paths call `LimitBandwidth`; rc calls can query or replace the current single limit.

## State and Persistence Behavior

State is process-local: current and previous limiter arrays, current timetable slot, and toggle flag. Scheduled updates replace `curr` or `prev` depending on SIGUSR2 toggle state.

## Dependencies and Integration Points

It depends on `golang.org/x/time/rate`, `fs.BwPair`/`BwTimetable`, rc, logging, and the Unix/non-Unix signal-handler files.

## Risks and Test Signals

Risks include burst-size overflow, schedule/toggle confusion, blocking on context.Background, rc accepting only one schedule entry, and inconsistent accounting versus transport limits. Tests cover rc set/query modes; integration tests should verify actual throttling and SIGUSR2 behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/token_bucket.go -->
