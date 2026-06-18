# sources/storage-engines/pebble/internal/cache/metrics.go

## Purpose
This file defines cache hit/miss dimensionality and exposes aggregate cache metrics, including lifetime and recent-window hit/miss counters.

## Important APIs, Types, And Functions
`NumLevels`, `Levels`, and `levelIndex` map unknown plus L0-L6 into metrics indexes. `Category` enumerates background, SSTable data, SSTable value, blob value, filter, and index accesses. `Metrics` reports `HitsAndMisses`, byte `Size`, object `Count`, and two `Recent` windows. `HitsAndMisses` supports `Get`, `Hits`, `Misses`, aggregate by all, level, category, and `ToRecent`. `Cache.Metrics` and `hitsAndMisses` read shard counters.

## Control Flow
Cache operations increment atomic per-shard counters. `Metrics` snapshots counters, locks each shard briefly to read block count and hot+cold size, then asks the metrics window for ten-minute and one-hour baselines and subtracts those from current totals.

## State And Persistence Behavior
Metrics are in-memory counters only. They persist for the lifetime of a `Cache` object and reset when a cache is recreated. Recent windows depend on `c.metricsWindow`, defined outside this file.

## Dependencies And Integration Points
The file uses `base.Level`, Go `iter.Seq`, and `crtime.Mono`. It integrates with `clockpro.go` counters, `cache.go` metrics window state, and external observability code.

## Risks And Edge Cases
The level/category indexes must stay aligned with all cache call sites. `CategoryHidden` is defined in `cache.go` and intentionally skips counter updates. Recent calculations assume monotonic current counters and may be misleading if baselines are newer than current snapshots due to misuse.

## Test Signals
The subset does not include metrics-specific tests. Indirect signals come from cache operations using valid level/category combinations and benchmarks randomizing through the index ranges.
