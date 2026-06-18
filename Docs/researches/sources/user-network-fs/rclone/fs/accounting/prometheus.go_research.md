<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/prometheus.go -->
# sources/user-network-fs/rclone/fs/accounting/prometheus.go

## Purpose

`prometheus.go` exposes rclone transfer statistics as a Prometheus collector.

## Important APIs, Types, and Functions

`RcloneCollector` stores descriptors for transferred bytes, speed, errors, checked/transferred files, deletes, deleted dirs, renames, listed entries, fatal error, and retry error. `NewRcloneCollector`, `Describe`, `Collect`, and `bool2Float` implement the collector surface.

## Control Flow

On collection, it builds a summed `StatsInfo` across groups, locks it, emits counters/gauges through `prometheus.MustNewConstMetric`, and unlocks.

## State and Persistence Behavior

The collector itself stores descriptors and context only. Metric values are snapshots of in-memory stats groups.

## Dependencies and Integration Points

It integrates with `github.com/prometheus/client_golang/prometheus`, stats-group aggregation, and any rclone rc/metrics server that registers the collector.

## Risks and Test Signals

Risks include metric-name compatibility, counter resets after stats reset, summed speed semantics, and lock contention during scrape. Tests should register the collector, mutate stats, gather metrics, and verify boolean gauges and counter values.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/fs/accounting/prometheus.go -->
