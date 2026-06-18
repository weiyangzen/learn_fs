<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups.go -->
# sources/user-network-fs/rclone/fs/accounting/stats_groups.go

## Purpose

`stats_groups.go` manages named stats groups and registers remote-control endpoints for listing, querying, resetting, deleting, and retrieving completed transfers.

## Important APIs, Types, and Functions

Exports include `WithStatsGroup`, `StatsGroupFromContext`, `Stats`, `StatsGroup`, `GlobalStats`, and `NewStatsGroup`. Internal `statsGroups` stores group map/order and supports set/get/names/sum/reset/delete. rc handlers are registered for `core/group-list`, `core/stats`, `core/transferred`, `core/stats-reset`, and `core/stats-delete`.

## Control Flow

Contexts may carry a stats group name. `Stats(ctx)` returns group stats or global stats, lazily creating groups as needed. rc handlers parse optional group/short parameters and either operate on a named group or a summed snapshot. `set` enforces `MaxStatsGroups` by evicting oldest non-global names.

## State and Persistence Behavior

Group state is in memory only. The global `groups` variable is initialized at package load. Reset clears all maps/order; delete removes one group after clearing its counters.

## Dependencies and Integration Points

It integrates with rclone rc, context propagation from operations/jobs, `StatsInfo`, global config, and Prometheus aggregation.

## Risks and Test Signals

Risks include returning the mutable `order` slice from `names`, group eviction surprises, aggregate snapshots starting goroutines via `NewStats`, and lock nesting between groups and stats. Tests cover group operations, rc calls, count-error routing, and memory behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/stats_groups.go -->
