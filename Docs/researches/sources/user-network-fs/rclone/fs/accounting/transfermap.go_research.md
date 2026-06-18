<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfermap.go -->
# sources/user-network-fs/rclone/fs/accounting/transfermap.go

## Purpose

`transfermap.go` manages live transfer/check maps and renders their human and rc progress views.

## Important APIs, Types, and Functions

`transferMap` wraps a mutex, map, and display name. Methods add/delete/merge entries, test emptiness/count, sort transfers by start time/name, render strings, compute aggregate progress from `inProgress`, list remotes, and build rc stat arrays.

## Control Flow

Stats code adds transfers when operations begin and deletes them on completion. Reporting paths sort current transfers, optionally exclude duplicates, look up active accounts for detailed byte/speed/ETA information, and otherwise print only the transfer purpose.

## State and Persistence Behavior

State is in memory and keyed by remote name. Merge copies transfer pointers for aggregate group views.

## Dependencies and Integration Points

It integrates with `StatsInfo.String`, `RemoteStats`, `inProgress`, `Transfer.rcStats`, and config-driven filename width.

## Risks and Test Signals

Risks include remote-name collisions, mutable pointer sharing in aggregate maps, lock nesting with exclude maps, and reporting stale/no-progress entries. Tests should cover sorting, exclusion, progress aggregation, and rc output.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/transfermap.go -->
