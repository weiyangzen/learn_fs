# sources/object-store/rustfs/crates/data-usage/src/data_usage.rs

## Purpose
This file contains the shared data-usage domain model and cache algorithms for RustFS. It represents capacity, bucket usage, object/version/delete-marker counts, histograms, replication summaries, per-disk status, and a hierarchical cache that can be merged, flattened, compacted, serialized, and converted into admin-facing `DataUsageInfo`.

## Important APIs, Types, and Functions
Core serializable types include `TierStats`, `AllTierStats`, `BucketTargetUsageInfo`, `BucketUsageInfo`, `DataUsageInfo`, and `DiskUsageStatus`. Cache types include `DataUsageHash`, `DataUsageEntry`, `DataUsageCacheInfo`, and `DataUsageCache`. Histogram types `SizeHistogram` and `VersionsHistogram` bucket object size and version-count distributions. Replication types include `ReplicationStats` and `ReplicationAllStats`. Important methods include `DataUsageCache::replace`, `replace_hashed`, `find`, `flatten`, `copy_with_children`, `delete_recursive`, `size_recursive`, `search_parent`, `force_compact`, `reduce_children_of`, `merge`, `dui`, `marshal_msg`, and `unmarshal`. `DataUsageInfo` exposes compatibility helpers such as `add_object`, `add_object_from_file_meta`, `update_capacity`, `add_bucket_usage`, `calculate_totals`, and `merge`.

## Control Flow
Cache writes hash cleaned paths and attach child hashes to parent entries. Read paths either find direct entries or recursively flatten children into aggregate usage. Compaction walks internal nodes, estimates descendant count, chooses candidates sorted by object count, flattens selected subtrees, marks them compacted, deletes descendants, and reinserts compacted summaries. `merge` combines roots, preserves the newest `last_update`, and merges or inserts flattened direct children from the other cache. `dui` flattens the requested path and each requested bucket into a `DataUsageInfo` response.

## State and Persistence
The cache persists as a `HashMap<String, DataUsageEntry>` plus `DataUsageCacheInfo`; `marshal_msg` and `unmarshal` use MessagePack via `rmp-serde`. Storage-specific load/save is intentionally abstracted behind the async `DataUsageCacheStorage` trait and implemented elsewhere. `SystemTime` is stored in info and admin responses. `failed_objects` and `disk_usage_status` are serde-defaulted for backward-compatible deserialization.

## Dependencies and Integration Points
The file depends on `path-clean` for canonical path keys, `serde` for API and cache serialization, `rmp-serde` for compact persistence, `async-trait` for backend storage integration, and `rustfs-filemeta` for converting object metadata and versions. E2e admin data-usage tests deserialize `DataUsageInfo` directly, so field names are part of a wire contract.

## Risks and Edge Cases
`DataUsageHash` uses cleaned path strings rather than cryptographic hashes, despite the type name. Some histogram naming differs between cache histograms and compatibility helpers (`LESS_THAN_1024_B` versus `0-1KB`), which can surprise consumers if both code paths feed the same UI. `DataUsageEntry::merge` clears existing replication target maps before adding other stats, which requires care when merging multiple sources. `extract_bucket_from_path` returns an empty string for paths beginning with `/`, because it only checks `parts.is_empty()`. Recursive flattening and deletion can be expensive for very large trees, hence compaction logic.

## Test Signals
Unit tests cover capacity updates, bucket merge totals, `SizeSummary::add`, cache merge inserting missing children, cache merge accumulating existing children, compaction candidate selection, leaf exclusion, subtree compaction, and saturating subtraction to prevent underflow during compaction. Broader behavioral coverage is supplied by admin data-usage e2e tests.
