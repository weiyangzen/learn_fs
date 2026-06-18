<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go -->
# sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go

## Purpose
Defines the operation labels used by the stats manager for component statistic updates.

## Important APIs, Types, and Functions
Constants `Increment`, `Decrement`, and `Replace` are string operation names consumed by `StatsCollector.UpdateStats` and interpreted by `statsDumper`.

## Control Flow and State
No runtime flow or state is present. The constants form a small shared contract between components producing stats and the stats manager consuming them.

## Dependencies and Integration Points
The package is `stats_manager`. Components should use these constants rather than hard-coded strings when reporting counters or gauges.

## Risks and Edge Cases
Because the constants are strings, callers can still pass invalid operations; `stats_manager.go` logs and ignores unknown operations. There is no type-level enum enforcement.

## Test Signals
Coverage comes indirectly through stats manager tests or component tests that call `UpdateStats`. This file has no standalone test surface.
<!-- END_FILE_RESEARCH: sources/user-network-fs/blobfuse2/internal/stats_manager/stats_common.go -->
