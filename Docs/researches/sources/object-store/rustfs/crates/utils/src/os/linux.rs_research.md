# sources/object-store/rustfs/crates/utils/src/os/linux.rs

## Purpose
Implements Linux disk information, physical-device identity, nested mount validation, and block IO statistics.

## Important APIs, Types, And Functions
`get_info` uses `rustix::fs::statfs` and `stat` to build `DiskInfo` with total/free/used bytes, inode counts, filesystem type, and device major/minor. `calculate_space_usage` handles reserved blocks and caps anomalous `bavail > bfree`. `same_disk` compares `st_dev`. `get_physical_device_ids` resolves `/sys/dev/block/<major>:<minor>` and recursively follows `slaves` to leaf devices. `check_cross_device_mounts` parses `/proc/mounts` and rejects nested child mount points under export paths. `get_drive_stats` reads `/sys/dev/block/<major>:<minor>/stat` into `IOStats`.

## Control Flow And State
The only persistent state is `BAVAIL_GT_BFREE_WARNING_PATHS`, a `OnceLock<Mutex<BTreeSet<PathBuf>>>` that limits warnings to once per path. Sysfs traversal falls back to `major:minor` when the sysfs link is absent. Mount validation normalizes paths to trailing-slash form before prefix comparisons.

## Dependencies And Integration Points
Uses `rustix`, `/sys`, `/proc/mounts`, `std::fs`, and `tracing::warn`. Re-exported from `os/mod.rs` on Linux and used by storage startup and health/diagnostic code that needs disk identity and capacity.

## Risks And Test Signals
Prefix mount checks are string-based and rely on normalized absolute paths; symlink/canonical path policy must be handled by callers. Device ID resolution depends on Linux sysfs layout and permissions. Tests cover device-mapper flattening, partition normalization, mount parsing, invalid export paths, fallback IDs, and several space-accounting edge cases.
