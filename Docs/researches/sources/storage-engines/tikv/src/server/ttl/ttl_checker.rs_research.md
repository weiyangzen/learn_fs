# sources/storage-engines/tikv/src/server/ttl/ttl_checker.rs

## Purpose

This module implements a timer-driven worker that scans region ranges for SST TTL properties and manually compacts fully expired files in the default column family. It also supports online updates to the scan interval.

## Important APIs, Types, And Functions

`Task::UpdatePollInterval(Duration)` is the worker control message. `TtlChecker<E, R>` holds a `KvEngine`, a `RegionInfoProvider`, and the current poll interval. `Runnable::run` updates the interval and the interval gauge. `RunnableWithTimer::on_timeout` performs a complete region scan round. `check_ttl_and_compact_files` reads TTL properties for a range and compacts expired files one at a time.

## Control Flow

`on_timeout` starts at an empty key and repeatedly calls `region_info_provider.seek_region` with a callback that scans up to 10 regions, reports start/end keys through an `mpsc` channel, and increments processed-region metrics. For each returned range, it converts region keys to data keys and calls `check_ttl_and_compact_files` with `exclude_l0=true`. It continues from the previous end key until an empty end key or no regions remain, then increments the finish metric, sleeps 40 seconds to let metrics be scraped, and resets the processed-region gauge.

`check_ttl_and_compact_files` gets range TTL properties from the engine. Empty properties count as `empty`; no expired files count as `skip`; expired files are compacted with `compact_files_cf(CF_DEFAULT, vec![file], None, 0, exclude_l0)`, with a two-second sleep between files.

## State And Persistence Behavior

The checker keeps only poll interval and cloned engine/provider handles. Persistent effects are RocksDB compactions that remove expired RawKV data and rewrite SST state. Metrics track interval, processed regions, action classes, and compaction duration.

## Dependencies And Integration Points

It depends on engine TTL properties and manual compaction APIs, raftstore `RegionInfoProvider`, TiKV worker traits, `UnixSecs`, and server TTL metrics. `StorageConfigManger` schedules `UpdatePollInterval` when online config changes.

## Risks And Edge Cases

Errors from `seek_region`, receiving from the callback channel, TTL property reads, and compaction are logged and counted, but the checker continues scanning where possible. `seek_region` callback communication is synchronous through a channel; if callback behavior changes, deadlock risk should be considered. The 40-second metrics sleep blocks the worker thread after each round. Expiration decisions use file-level max expire timestamp, so files with any unexpired entries are skipped.

## Test Signals

No local tests are present in this file. Test signals are mainly metrics and integration behavior through engines that expose TTL properties and compaction.
