# sources/object-store/rustfs/crates/scanner/src/data_usage_define.rs

## Purpose

`data_usage_define.rs` defines the scanner's data-usage cache model, size/replication/tier accounting helpers, persisted cache paths, scan checkpoint metadata, and cache load/save behavior. It is the main in-crate bridge between `rustfs_data_usage` aggregate types and scanner-specific persistence rules. The file also re-exports core data-usage types (`DataUsageInfo`, `DataUsageEntry`, `DataUsageHash`, `BucketUsageInfo`, etc.) so the scanner crate can expose the data-usage API through `lib.rs`.

## Important APIs, Types, and Functions

- Constants and paths:
  - `DATA_USAGE_ROOT`, `DATA_USAGE_CACHE_NAME`, `DATA_USAGE_SCAN_CHECKPOINT_VERSION`.
  - `DATA_USAGE_BUCKET`, `DATA_USAGE_OBJ_NAME_PATH`, `DATA_USAGE_BLOOM_NAME_PATH`, and `BACKGROUND_HEAL_INFO_PATH` are `LazyLock<String>` values built from the meta bucket and bucket metadata prefix.
  - Internal object names include `.usage.json`, `.bloomcycle.bin`, `.usage-cache.bin`, and `.bloomcycle.bin`.
- Accounting types:
  - `TierStats` tracks size, versions, and latest object count per storage tier. `from_object_info` converts an `ObjectInfo` into one version of tier usage.
  - `AllTierStats` merges and populates tier maps.
  - `SizeSummary` accumulates object/version/delete-marker totals, replication status sizes/counts, per-target replication stats, and per-tier stats.
  - `ReplTargetSizeSummary` is the per-replication-target portion of `SizeSummary`.
- Checkpoint types:
  - `DataUsageScanCheckpointReason` serializes as snake_case values `runtime`, `objects`, `directories`, and `unknown`.
  - `DataUsageScanCheckpoint` records `version`, `resume_after`, and `reason`; `new` stamps the current checkpoint version.
  - `DataUsageCacheInfo` includes bucket/cache metadata, lifecycle and replication configs, failed-object counts, old `scan_resume_after`, and newer structured `scan_checkpoint`.
- `DataUsageCache` is the central cache structure:
  - `replace` and `replace_hashed` insert entries and wire parent child references.
  - `find`, `find_children_copy`, `root`, and `root_hash` are lookup helpers.
  - `flatten`, `size_recursive`, and `dui` collapse child trees into aggregate usage information.
  - `copy_with_children`, `delete_recursive`, `search_parent`, `is_compacted`, `force_compact`, `reduce_children_of`, `total_children_rec`, and `merge` maintain or reduce cache tree state.
  - `marshal_msg` and `unmarshal` use MessagePack via `rmp_serde` for scanner cache persistence.
  - `load` and `save` handle object-store persistence with timeouts, retries, fallback paths, backup writes, logging, and metrics.
- `DataUsageCacheStorage` is an async trait placeholder for storage-specific cache load/save implementations, but this file does not provide a concrete implementation.

## Control Flow

Cache mutation starts with hashed path insertion. `replace_hashed` inserts the entry by `DataUsageHash::key()` and, when a parent is present, ensures the parent entry exists and records the child hash. Read-side aggregation starts at a found entry, recursively `flatten`s descendants, merges their `DataUsageEntry` counters, and clears children from the returned aggregate so callers receive a compact summary rather than a tree.

`dui` converts an arbitrary cached path plus a bucket list into a `DataUsageInfo`: it flattens the requested path for global totals, then flattens each bucket for per-bucket `BucketUsageInfo`, including histograms and replication target details when present.

Compaction follows two paths. `force_compact` triggers only when cache length reaches a caller-provided limit; it may compact a very large top-level child list, then retains only reachable nodes from the top entry. `reduce_children_of` computes recursive child pressure, collects internal nodes with `add`, sorts candidates by object count, and replaces selected subtrees with compacted flat entries until enough children have been removed. It uses saturating subtraction to avoid underflow when one candidate removes more children than the remaining target.

`load` resets the receiver to default, attempts the main cache object up to five times, and tries a `.bkp` object between retries. The lower-level `try_load_inner` first reads from `RUSTFS_META_BUCKET/<bucket-meta-prefix>/<name>`, then falls back to `DATA_USAGE_BUCKET/<name>` for compatibility. Not-found and decode failures return empty cache without hard failure; quorum, faulty disk, full disk/storage, slowdown, and timeout are treated as retryable; other storage errors are returned.

`save` serializes to MessagePack, writes the main object under the bucket metadata prefix with the configured cache-save timeout and two retries, then attempts a `.bkp` write with timeout capped at five seconds and no retries. Main save failure is returned; backup save failure is logged but not fatal.

## State and Persistence Behavior

The cache is an in-memory `HashMap<String, DataUsageEntry>` keyed by data-usage hash strings, plus `DataUsageCacheInfo` metadata. Parent-child links are duplicated inside `DataUsageEntry.children`; callers must keep those links consistent when replacing or deleting nodes. `find_children_copy` has the side effect of creating an empty cache entry for missing hashes.

Scanner cache persistence uses MessagePack, while the higher-level scanner data-usage snapshot in `scanner.rs` uses JSON. The cache loader is intentionally optimistic and lock-free because scanner data is background-maintained. It handles old serialized forms by defaulting missing `scan_resume_after` and `scan_checkpoint` fields. Save metrics are registered once and emitted with labels for main vs backup cache and result states success/error/timeout.

Checkpoint fields support partial scan resume in `scanner_folder.rs`: `scan_resume_after` is the older simple marker, while `scan_checkpoint` adds version and stop reason. This file owns the serialized schema and compatibility defaults, not the scan-resume algorithm itself.

## Dependencies and Integration Points

- Re-exports and composes `rustfs_data_usage` types.
- Reads object metadata from `rustfs_ecstore::store_api::ObjectInfo` and object-store IO via `ObjectIO`.
- Persists through `rustfs_ecstore::config::com::save_config` and object readers.
- Uses lifecycle and replication config types in `DataUsageCacheInfo`, with `TRANSITION_COMPLETE` and `storageclass::STANDARD` used for tier accounting.
- Uses `runtime_config::scanner_cache_save_timeout()` for save timeout behavior.
- Emits `metrics` counters/histograms and structured `tracing` warnings.
- Used heavily by `scanner_io.rs` and `scanner_folder.rs` for namespace scanning, partial caches, checkpointing, and cache merging.

## Risks and Edge Cases

- Cache parent-child consistency is manual; direct map edits can orphan entries or leave stale child references.
- `find_children_copy` mutates missing paths by inserting a default entry, which can surprise callers expecting a pure read.
- `SizeSummary::actions_accounting` appears to call `tier_stats.add(...)` without assigning the returned `TierStats`; because `TierStats::add` returns a new value rather than mutating `self`, existing tier entries may not be updated as intended.
- Load treats deserialization failures as empty cache rather than surfacing corruption, so bad cache data may silently trigger full rebuild behavior.
- Lock-free cache load/save means readers can observe stale or partially superseded scanner data; backup and retry logic mitigate but do not provide transactional persistence.
- The compatibility fallback path in `try_load_inner` reads from two locations. Future path changes must keep this dual lookup in mind to avoid losing existing deployments.
- Backup save is best-effort. A successful main write followed by failed backup write is considered success.
- Compaction chooses candidates by object count, not size or operational value; compacting small-object internal nodes first may not minimize memory in all workloads.

## Test Signals

The module has focused unit tests for data-usage merging, defaulting old serialized cache info, cache tree mutation, recursive copy/delete, missing-child lookup side effects, cache path classification, cache save timeout environment behavior, retry save success and timeout failure, and compaction candidate/underflow behavior. These tests signal that compatibility with older serialized cache shapes, bounded save behavior, and compaction correctness are important maintenance contracts.
