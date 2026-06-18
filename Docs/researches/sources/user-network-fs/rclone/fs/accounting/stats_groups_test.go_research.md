<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go

## Purpose

`stats_groups_test.go` validates stats group storage, aggregation, rc endpoints, memory behavior, and `fs.CountError` routing.

## Important APIs, Types, and Functions

The suite exercises `newStatsGroups`, set/get/names/sum/reset/delete behavior, `NewStatsGroup`, rc calls for `core/group-list`, `core/stats`, `core/transferred`, `core/stats-reset`, `core/stats-delete`, and helper `percentDiff`.

## Control Flow

Tests construct independent group containers, add `StatsInfo` instances, mutate counters/transfers, call rc handlers through `rc.Calls`, and compare results. `TestCountError` temporarily replaces the global `groups` container and calls `Start` to install `fs.CountError`.

## State and Persistence Behavior

The tests manipulate global `groups` and global error-count hook, so cleanup/isolation is important. Memory-oriented assertions compare heap object counts after many groups.

## Dependencies and Integration Points

It integrates with `mockobject`, rc call registry, contexts carrying stats group names, and global accounting initialization.

## Risks and Test Signals

Signals include correct grouping, aggregate rc values, completed-transfer reporting, reset/delete effects, and error attribution. Race tests should watch global group replacement and rc calls in parallel.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups_test.go -->
