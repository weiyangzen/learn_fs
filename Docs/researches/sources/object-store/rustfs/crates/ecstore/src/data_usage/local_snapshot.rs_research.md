# sources/object-store/rustfs/crates/ecstore/src/data_usage/local_snapshot.rs

## Purpose
This file defines the local per-disk data-usage snapshot format and filesystem helpers used by scanner/accounting code.

## Important APIs, types, and functions
Exports include `DATA_USAGE_DIR`, `DATA_USAGE_STATE_DIR`, `LOCAL_USAGE_SNAPSHOT_VERSION`, `LocalUsageSnapshotMeta`, `LocalUsageSnapshot`, `snapshot_file_name`, `snapshot_object_path`, `data_usage_dir`, `data_usage_state_dir`, `snapshot_path`, `read_snapshot`, `write_snapshot`, and `ensure_data_usage_layout`. `LocalUsageSnapshot::new` fills the format version, and `recompute_totals` derives cached totals from per-bucket usage.

## Control flow
Writers create/populate a snapshot, recompute totals, and call `write_snapshot`, which creates the datausage directory and writes pretty JSON to `<disk-id>.json`. Readers call `read_snapshot`, receiving `Ok(None)` for missing files and an error for unreadable or malformed JSON. Layout creation ensures both snapshot and state directories exist.

## State and persistence behavior
Snapshots live under `<root>/<RUSTFS_META_BUCKET>/datausage/<disk-id>.json`; scanner state uses `datausage/state`. Writes overwrite existing files and are not atomic. Format version is stored but not checked on read.

## Dependencies and integration points
It depends on `BucketUsageInfo`, metadata bucket naming, ecstore errors, `serde`, `tokio::fs`, and path/time types. `data_usage.rs` re-exports and aggregates these snapshots.

## Risks and edge cases
Partial writes can produce corrupt JSON; aggregation may then delete the file. Newer format versions are not explicitly gated. Disk IDs are used in filenames and must be path-safe. `SystemTime` serialization compatibility depends on serde behavior.

## Test signals
No local tests cover filesystem behavior. `data_usage.rs` tests indirectly exercise `new` and `recompute_totals` through aggregation fixtures.
