# sources/storage-engines/tikv/src/server/gc_worker/config.rs

## Purpose

This file defines runtime configuration for GC, compaction-filter GC, and automatic compaction. It also provides the online config manager that updates the version-tracked config and resizes the GC worker future pool when `num_threads` changes.

## Important APIs, Types, And Functions

- `AutoCompactionConfig` controls automatic compaction interval, tombstone thresholds, redundant-row thresholds, bottommost force, and MVCC-read-aware scoring.
- `AutoCompactionConfig::default` uses raftstore-like defaults: 5-minute checks, 10k tombstones, 30 percent tombstones, 50k redundant rows, 20 percent redundant rows, bottommost force off, MVCC read awareness off, scan threshold 1000, and read weight 3.0.
- `AutoCompactionConfig::validate` rejects zero intervals, percentage thresholds over 100, and negative MVCC read weight.
- `GcConfig` controls traditional GC ratio threshold, batch size, write bandwidth limit, compaction filter enablement and version-check override, worker thread count, and nested auto-compaction config.
- `GcConfig::validate` rejects zero batch size and zero thread count, then validates auto-compaction.
- `GcWorkerConfigManager` wraps `Arc<VersionTrack<GcConfig>>` and optional `FuturePool`.
- `ConfigManager::dispatch` applies online changes and scales the pool when `num_threads` is updated.

## Control Flow

Configuration is deserialized with kebab-case field names and defaults. Online config changes are cloned, inspected for `num_threads`, optionally applied to the worker future pool with `scale_pool_size`, then committed into `VersionTrack` through `OnlineConfig::update`. The manager logs both thread-count changes and the final change payload.

## State And Persistence Behavior

The file has no direct persistence. Runtime state lives in `VersionTrack<GcConfig>` so workers can track config versions without global locks. The optional pool reference lets config dispatch affect live concurrency. `ReadableDuration` and `ReadableSize` carry human-readable config units.

## Dependencies And Integration Points

It integrates `online_config`, `tikv_util::config::{ReadableDuration, ReadableSize, VersionTrack}`, and `yatp_pool::FuturePool`. `GcWorker`, `GcManager`, `CompactionRunner`, and `WriteCompactionFilterFactory` read this config through trackers and snapshots.

## Risks

- `ratio_threshold` is not validated here; downstream code treats negative or infinite values as disabling GC and values below 1.0 as always GC.
- MVCC read weight can be arbitrarily high, potentially over-prioritizing read-hot regions.
- Pool scaling is applied before the version-track update; if config update later failed, the pool would already be resized.
- `num_threads` field is logged as `gc.thread_count` in validation text, which may not exactly match the serialized field name.

## Test Signals

Direct tests are not in this file. `gc_worker.rs` contains `test_update_gc_thread_count`, which dispatches online `num_threads` changes and verifies the worker pool size changes from 1 to 5 and then to 2.
