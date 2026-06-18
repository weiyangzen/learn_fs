# sources/object-store/rustfs/crates/ecstore/src/store_init.rs

## Purpose

`store_init.rs` handles erasure-store disk connection and format initialization. It opens configured endpoints, loads `format.json` from all disks, validates format quorum and erasure layout, initializes completely unformatted deployments on the first disk path, migrates compatible MinIO format metadata when present, saves new format files atomically, and exposes helper logic for default parity calculation.

## Important APIs, Types, and Functions

- `init_disks` asynchronously calls `new_disk` for every endpoint and returns parallel vectors of `Option<DiskStore>` and `Option<DiskError>`.
- `connect_load_init_formats` is the main bootstrap coordinator. It loads all formats, checks fatal disk errors and format validity, initializes or migrates when all disks are unformatted and this is the first disk, waits/errors appropriately for first-disk coordination, and otherwise returns a quorum format.
- `quorum_unformatted_disks`, `should_init_erasure_disks`, and `check_disk_fatal_errs` classify disk error sets.
- `init_format_erasure` builds a new `FormatV3`, assigns `erasure.this` per set/drive slot, applies an optional deployment UUID, writes all format files, and returns the quorum format.
- `try_migrate_format` searches existing disks for MinIO migrating metadata, validates expected set count, drive count, and erasure version, rewrites per-disk `erasure.this`, saves RustFS format files, and returns the quorum format.
- `get_format_erasure_in_quorum` selects the format layout with majority drive-count agreement, clones a representative, and clears `erasure.this` to nil before returning it as the cluster-level format.
- `check_format_erasure_values` and `check_format_erasure_value` validate meta version, erasure version, total format count, and set drive count.
- `load_format_erasure_all` and `load_format_erasure` read format files across disks, map missing format files to `UnformattedDisk`, optionally attach disk info for healing, and set disk IDs when not healing.
- `save_format_file_all` and `save_format_file` write format JSON through a temporary UUID-named file, rename it to the canonical format file, set the disk ID, and reduce write errors by quorum.
- `ec_drives_no_config` computes default parity for a set drive count via storage-class config defaults.

## Control Flow

Bootstrap starts with `init_disks`, which fans out endpoint connection attempts and preserves endpoint order in disk/error vectors. `connect_load_init_formats` then loads formats from available disks. If every disk has a fatal homogeneous error such as unsupported disk, access denied, or non-directory path, startup fails immediately. Existing format values are validated before any init decision.

When `first_disk` is true and every disk is unformatted, the code first tries `try_migrate_format`. Migration reads `FORMAT_CONFIG_FILE` from `MIGRATING_META_BUCKET` on each available disk until it finds parseable data. It rejects layout mismatches and non-V3 erasure formats, then constructs per-disk cloned formats with slot-specific `erasure.this`, saves them to RustFS metadata, and returns quorum. If migration fails, `init_format_erasure` creates a new format and writes one slot-specific copy per disk.

If a quorum of disks is unformatted but not all disks are ready for initialization, `connect_load_init_formats` returns coordination errors: `NotFirstDisk` for non-first disk callers and `FirstDiskWait` for first-disk callers waiting on partial formatting. Otherwise it selects the format in quorum and returns it.

Format save uses a two-step write: write JSON to a UUID temporary object under the RustFS metadata bucket, then rename to `FORMAT_CONFIG_FILE`. `save_format_file_all` performs all saves concurrently and applies `reduce_write_quorum_errs` over the result vector.

## State and Persistence Behavior

This file directly persists cluster format state. It reads `FORMAT_CONFIG_FILE` from `RUSTFS_META_BUCKET` and migration candidates from `MIGRATING_META_BUCKET`. It writes new format JSON to a temporary object then atomically renames it to the canonical format path on each disk, and updates each `DiskStore`'s in-memory disk ID with the slot UUID. Returned cluster-level formats intentionally set `erasure.this` to nil so callers do not treat one disk's slot ID as global state. In heal mode, `load_format_erasure` attaches live disk info to the loaded `FormatV3`.

## Dependencies and Integration Points

The module depends on disk APIs (`DiskStore`, `DiskAPI`, `new_disk`, `DiskOption`, `DiskInfoOptions`, `DiskError`, metadata bucket constants), format types (`FormatV3`, `FormatMetaVersion`, `FormatErasureVersion`), quorum helpers (`count_errs`, `reduce_write_quorum_errs`), endpoint configuration, storage-class config (`lookup_config`, `STANDARD`), `futures::join_all`, `uuid::Uuid`, and tracing. It is part of startup and healing paths for erasure-coded object storage, and its output `FormatV3` determines set/drive topology for higher-level erasure sets.

## Risks and Edge Cases

- `check_format_erasure_values` validates each present format against the total number of disk slots; mixed or stale formats can block startup before quorum selection.
- `get_format_erasure_in_quorum` groups only by `drives()` count, not by full deployment ID or complete set topology. That may be sufficient for current `FormatV3::drives` semantics, but it is a sensitive quorum criterion.
- Migration uses the first compatible MinIO format found. If multiple disks carry divergent but layout-compatible migrating formats, the first one in disk order wins.
- `save_format_file_all` indexes `formats[i]` for every disk, so caller-provided format vectors must exactly match disk length.
- The temporary-write then rename sequence depends on disk backend rename semantics for atomicity.
- Missing disk stores are represented as `DiskNotFound`, which participates in quorum reduction rather than being filtered out.
- The bootstrap state machine distinguishes all-unformatted from quorum-unformatted; partial unformatted deployments return coordination errors rather than initializing.

## Test Signals

No tests are defined in this file. Existing confidence likely comes from disk/format integration tests elsewhere. Useful focused tests would cover all-unformatted first-disk initialization, partial unformatted coordination errors, fatal homogeneous disk errors, quorum selection with mixed formats, migration from MinIO metadata, write quorum reduction, and validation failures for mismatched set sizes or erasure versions.
