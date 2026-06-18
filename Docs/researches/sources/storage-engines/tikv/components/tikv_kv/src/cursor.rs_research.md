# sources/storage-engines/tikv/components/tikv_kv/src/cursor.rs

## Purpose
This file defines `Cursor`, TiKV's higher-level wrapper around engine iterators. It adds scan-mode semantics, near-seek optimization, prefix-seek handling, key/value read accounting, iterator error handling, and a builder for snapshot cursors.

## Important APIs, Types, and Control Flow
`Cursor<I>` stores an engine iterator, `ScanMode`, prefix-seek flag, min/max miss guards, read flags for flow statistics, and an optional missing-range cache. `seek` finds the first key greater than or equal to a target for forward/mixed scans; `seek_for_prev` finds the last key less than or equal to a target for backward/mixed scans. `near_seek` and `near_seek_for_prev` walk with `next` or `prev` while the cursor is near the target, falling back to full seek after `SEEK_BOUND`. `reverse_seek` and `near_reverse_seek` implement strict-less-than target positioning.

The missing-range cache is enabled only for mixed, non-prefix cursors. When a seek lands at an upper key greater than the target, `[target, upper)` can be cached as empty while the iterator remains at `upper`. Later seeks inside that range skip extra iterator movement. `key` and `value` update `CfStatistics` only once per cursor position. Iterator movement wraps stats collection by operation kind. `valid` converts iterator status errors into critical metrics, optional panic marks, or logged errors.

`CursorBuilder` converts optional lower/upper `Key` bounds into `KeyBuilder` bounds, configures `IterOptions` for fill-cache, prefix seek, timestamp hints, key-only reads, and max skippable internal keys, then creates a `Cursor`.

## State, Dependencies, and Integration
Cursor state is transient over a snapshot iterator. It integrates with `engine_traits::IterOptions`, TiKV key encoding, `CfStatistics`, RocksDB iterator metrics, failpoints, critical error metrics, and `Snapshot`. Prefix seek is restricted from `seek_to_first` and `seek_to_last`.

## Risks and Test Signals
Risks include stale missing-range caches, incorrect min/max miss shortcuts, prefix-seek end semantics, scan-mode misuse, and panics from invalid iterator assumptions. Tests cover prefix seek behavior, many missing-range cache hit/miss and invalidation cases with statistics assertions, and reverse iteration over region snapshots.
