# sources/object-store/rustfs/crates/ecstore/src/set_disk/heal.rs

## Purpose
Implements object and object-directory healing for a single erasure set. It repairs missing or stale shards by reading quorum metadata, selecting the latest valid `FileInfo`, reconstructing data through erasure coding, writing healed shards under `.rustfs/tmp`, and atomically renaming them back to the bucket/object path. It also builds `HealResultItem` status before/after drive state.

## Important APIs, Types, And Functions
The main API is `SetDisks::heal_object(bucket, object, version_id, opts)`, returning a `HealResultItem` and optional `DiskError`. `heal_object_dir_locked` and `heal_object_dir` repair missing object directories, optionally removing dangling directories. `default_heal_result` renders drive state when normal healing cannot proceed. The implementation depends heavily on `FileInfo`, `ObjectInfo`, `HealOpts`, `HealDriveInfo`, `DriveState`, erasure coding readers/writers, `read_all_fileinfo`, `object_quorum_from_meta`, `list_online_disks`, `pick_valid_fileinfo`, `disks_with_all_parts`, and `delete_if_dangling`.

## Control Flow
`heal_object` optionally takes a namespace write lock, reads all versions/metadata, exits early for all-not-found, computes read/write quorum from metadata, filters online disks by common mod time or ETag, and picks the quorum `FileInfo`. It marks drives as ok/missing/corrupt/offline, exits on dry-run or no-op, checks whether data or metadata loss exceeds parity tolerance, and deletes dangling versions if repair is impossible. For repairable data, it shuffles disks by erasure distribution, cleans metadata for target drives, reconstructs each part from bitrot readers to bitrot writers, updates `FileInfo` checksums/inline data, and renames healed temp data to the final location.

## State And Persistence Behavior
State changes are persisted by `rename_data` on each outdated disk and by optional deletes of remote data directories or dangling versions. Temporary data is written beneath `RUSTFS_META_TMP_BUCKET` using a UUID and cleaned with `delete_all`. The function mutates the result’s drive states after successful rename and records capacity scope for healed disks.

## Dependencies And Integration Points
This file integrates namespace locks, disk APIs, erasure coding, storage-class inline decisions, environment-controlled zero-copy reads, heal-channel types, object metadata consensus helpers, and object deletion logic. It is called through `Sets::heal_object` and `ECStore::handle_heal_object`.

## Risks
There is complex index alignment between disks, metadata, part-error maps, and erasure distribution; mistakes can heal the wrong shard. `latest_meta.data_dir.unwrap()` assumes a data directory for non-deleted local objects. `default_heal_result` pushes offline entries and then pushes another state for every disk, which may duplicate drive entries for offline disks. Temp cleanup occurs after each rename attempt, so partial failures require careful validation.

## Test Signals
No local tests in this file. Coverage is indirect through read/write/quorum helper tests and higher-level heal paths. Strong regression tests would cover stale metadata-only repair, data shard reconstruction, dry-run, dangling deletes, distribution mismatch refusal, and offline disk result rendering.
