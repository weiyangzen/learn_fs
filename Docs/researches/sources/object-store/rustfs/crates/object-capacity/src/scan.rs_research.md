<!-- BEGIN_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/scan.rs -->
# sources/object-store/rustfs/crates/object-capacity/src/scan.rs

## Purpose
Implements the filesystem scanning path behind capacity refreshes. It computes used bytes and file counts across one or more disk roots, supports exact and sampled estimates, handles partial disk failures, and produces per-disk updates for incremental dirty-disk refreshes.

## Important APIs, Types, and Functions
`scan_used_capacity_disks` is the public summary API. `calculate_data_dir_used_capacity_report` parallelizes per-disk scans and aggregates a `CapacityScanReport`. `select_capacity_refresh_disks` decides whether a manager can refresh only dirty disks. `refresh_capacity_with_scope` converts scan reports into `CapacityUpdate`. Internal structures include `DiskScanOutcome`, `DiskCapacityScanResult`, `SymlinkTracker`, and `ProgressMonitor`.

## Control Flow
Disks are scanned via a futures stream with `buffer_unordered` and a maximum concurrency of four. Each disk scan calls `get_dir_size_async`, which runs a blocking `WalkDir` traversal in `spawn_blocking`. For each regular file, it updates exact prefix bytes until `max_files_threshold`; after that, it samples overflow files by `sample_rate` and estimates total size. Progress checks run every 512 files and can terminate with timeout or stall detection. If sampling data exists when a timeout occurs, the function returns a fallback estimate instead of failing.

## State and Persistence
The scanner itself is stateless across calls. It reads capacity config from `capacity_manager` helpers and returns in-memory scan summaries. Partial traversal or metadata failures are recorded in the result and influence whether per-disk cache updates can be committed.

## Dependencies and Integration
Uses `walkdir`, Tokio blocking tasks, `futures` streams, capacity metrics, and tracing. It integrates with `HybridCapacityManager` by selecting refresh scopes and returning `CapacityUpdate` values with per-disk cache replacement or dirty-disk clearing metadata.

## Risks
Sampling can under- or over-estimate when overflow files differ significantly from sampled files. Symlink tracking records targets but relies on `WalkDir` for actual traversal behavior; path cycles and depth limits deserve operational scrutiny. A dirty subset refresh with partial errors is rejected, so repeated disk-specific failures can keep dirty state uncleared.

## Test Signals
Tests cover empty, single-file, multi-file, nested directory, nonexistent path, partial multi-disk success, full-versus-dirty disk selection based on complete cache state, and Unix symlink inclusion/exclusion under env-controlled follow settings.
<!-- END_FILE_RESEARCH: sources/object-store/rustfs/crates/object-capacity/src/scan.rs -->
