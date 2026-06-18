<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/inprogress.go -->
# sources/user-network-fs/rclone/fs/accounting/inprogress.go

## Purpose

`inprogress.go` stores the mapping from remote names to live `Account` objects for progress display and remote-control stats.

## Important APIs, Types, and Functions

The `inProgress` type wraps a mutex and `map[string]*Account`. Methods create the map sized from `ci.Transfers`, set, clear, get, and merge entries from another in-progress map.

## Control Flow

`newAccountSizeName` inserts an account on start, `Account.Done` clears it, and stats/reporting code consults the map to enrich `transferMap` output with byte/speed/ETA data.

## State and Persistence Behavior

State is process-local and keyed by remote path. Duplicate remote names overwrite each other, so concurrent same-name transfers can hide one progress entry.

## Dependencies and Integration Points

It integrates with `StatsInfo`, `transferMap`, stats group aggregation, and rc stats rendering.

## Risks and Test Signals

Risks include same-name collisions, map copying while transfers mutate, and stale entries if `Done` is skipped. Tests should cover set/clear/get/merge and duplicate remote behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/inprogress.go -->
