# sources/object-store/rustfs/crates/object-capacity/benches/capacity_scan.rs

## Purpose
Criterion benchmark for `scan_used_capacity_disks`, measuring exact single-disk scans, sampled large scans, and mixed multi-disk scans using temporary filesystem fixtures.

## Important APIs, types, and functions
- Constants define exact file size (4 KiB), sampled file size (1 byte), and sampling trigger file count (202,048).
- `DiskSpec` describes fixture file count and size.
- `CapacityScanFixture` owns temp dirs and `CapacityDiskRef` entries.
- `populate_files` creates sharded bucket directories and object files with fixed payloads.
- `bench_capacity_scan` builds a current-thread tokio runtime, creates fixtures, and registers Criterion groups.
- Bench target uses `criterion_group!` and `criterion_main!`.

## Control flow
Fixture construction creates temp directories, populates files, and records drive paths. The benchmark creates one exact 10k-file fixture, one sampled 202k-file fixture, and one four-disk mixed fixture. Each Criterion bench blocks on `scan_used_capacity_disks`, black-boxing disk refs and summaries.

## State and persistence behavior
State is temporary filesystem content under `TempDir`; directories remain alive for the fixture lifetime through `_dirs`. No repository or production state is modified. The sampled fixture intentionally creates many tiny files to cross the scanner's sampling threshold.

## Dependencies and integration points
Depends on `rustfs_object_capacity::{CapacityDiskRef, scan_used_capacity_disks}`, Criterion, Tokio runtime, `tempfile`, standard filesystem APIs, and `black_box`.

## Risks and edge cases
The benchmark creates over 200k files, so setup can be slow and filesystem-dependent. Results will vary by storage backend, directory entry caching, and OS. The sharding formula clamps bucket directory count between 1 and 256, giving broad directory coverage without one file per directory.

## Test signals
Criterion output provides performance timing for `capacity_scan_exact/single_disk_10k_4k`, `capacity_scan_sampled/single_disk_202k_1b`, and `capacity_scan_multi_disk/four_disks_mixed_exact`. Successful benchmark setup also validates scanner compatibility with multiple temp disk roots.
