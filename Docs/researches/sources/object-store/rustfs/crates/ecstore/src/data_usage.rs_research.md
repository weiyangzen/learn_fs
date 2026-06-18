# sources/object-store/rustfs/crates/ecstore/src/data_usage.rs

## Purpose
This module manages ecstore data-usage accounting. It persists cluster summaries, loads them with compatibility repair, aggregates local disk snapshots, computes bucket usage by listing, maintains a memory overlay for fresh quota/admin reads, and handles binary `DataUsageCache` files.

## Important APIs, types, and functions
Key APIs are `store_data_usage_in_backend`, `load_data_usage_from_backend`, `aggregate_local_snapshots`, `compute_bucket_usage`, memory update/read helpers, `replace_bucket_usage_memory_from_info`, `apply_bucket_usage_memory_overlay`, `sync_memory_cache_with_backend`, `create_cache_entry_from_summary`, `cache_to_data_usage_info`, `load_data_usage_cache`, and `save_data_usage_cache`. It re-exports local snapshot helpers.

## Control flow
Backend writes JSON to `buckets/.usage.json` and skip older/equal `last_update` data. Loads read primary, record system-path failure metrics, fall back to `.bkp`, default on missing config, repair old `bucket_sizes`/`buckets_usage`, and migrate legacy replication counters. Snapshot aggregation walks pools/sets/local disks, deduplicates disks, reads snapshots, deletes corrupted files best-effort, fills missing meta, and merges totals. Memory overlay hydrates from backend, updates on writes/deletes, refreshes by TTL, and overlays newer in-memory entries onto persisted responses.

## State and persistence behavior
Persistent state includes `.usage.json`, `.usage.json.bkp`, `.usage-cache.bin`, async backup cache writes, and per-disk local snapshots. Process state is `USAGE_MEMORY_CACHE` plus `USAGE_CACHE_UPDATING`, storing refresh and usage-update timestamps to protect newer memory mutations from older backend/scanner data.

## Dependencies and integration points
It depends on `rustfs_data_usage`, config read/write helpers, `ECStore` topology, disk APIs, object listing, bucket replication config, system-path failure metrics, `GLOBAL_OBJECT_API`, and `resolve_object_store_handle`.

## Risks and edge cases
The overlay is process-local and lost on restart. TTL refresh can return stale values. Corrupted snapshots are deleted. `compute_bucket_usage` is list-based and may not be a complete versioned audit. Backup writes are spawned and ignored. Binary cache decode failure can collapse to default cache without explicit corruption reporting.

## Test signals
Tests cover corrupted snapshot aggregation, delete overlay, overwrite count preservation, newer persisted usage suppressing memory overlay, and scanner sync preserving newer memory updates. Backend load/write, replication migration, full disk traversal, exact bucket listing, and binary cache I/O are not directly covered.
