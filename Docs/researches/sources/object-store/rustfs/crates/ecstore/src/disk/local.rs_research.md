# sources/object-store/rustfs/crates/ecstore/src/disk/local.rs

## Purpose
This file implements the concrete local filesystem backend for the `DiskAPI` abstraction used by RustFS erasure-coded object storage. It maps bucket/object/version operations to directories, `xl.meta` metadata files, erasure data directories, temporary staging paths, and the `.rustfs.sys` control tree on a mounted local disk. It is the main persistence boundary for local disks: it validates endpoint identity against `format.json`, performs object part verification, writes and updates RustFS file metadata, walks object namespaces, handles delete/trash cleanup, and exposes disk capacity/state information.

## Important APIs, types, and functions
`LocalDisk` holds the disk root, `.rustfs.sys/format.json` path, cached `FormatInfo`, endpoint identity, disk-info cache, scan counter, path cache, startup-cleanup latch, and background cleanup exit signal. `FormatInfo` caches the disk UUID, serialized format bytes, filesystem metadata, and last freshness check. `InternalBuf` allows internal writes from borrowed bytes or owned `Bytes`.

`FileCacheReclaimReader` and `FileCacheReclaimWriter` wrap `tokio::fs::File` and optionally call Linux `fadvise(DontNeed)` after large reads/writes or macOS `F_NOCACHE`; metrics are emitted through `rustfs_page_cache_reclaim_*`. The reclaim thresholds are driven by `rustfs_config` environment variables.

`LocalDisk::new` is the constructor. It resolves the endpoint root, ensures the data-usage layout, optionally moves stale startup temp state aside, loads and validates `format.json`, builds a one-second `Cache<DiskInfo>`, creates required metadata volumes, and spawns the deleted-object cleanup loop.

Path helpers include `resolve_local_disk_root`, `resolve_abs_path`, `get_object_path`, `get_bucket_path`, `check_valid_path`, `get_object_paths_batch`, and `normalize_path_components`. These enforce root confinement and optimize repeated path construction through a `parking_lot::RwLock<HashMap<...>>`.

Persistence helpers include `read_raw`, `read_metadata_with_dmtime`, `read_all_data_with_dmtime`, `write_all_meta`, `write_all_public`, `write_all_private`, `write_all_internal`, `open_file`, and `read_file_exists`. Object metadata operations are implemented through `rustfs_filemeta::FileMeta`, `FileInfo`, `RawFileInfo`, and helpers such as `get_file_info`.

Cleanup and deletion are handled by `cleanup_tmp_on_startup`, `cleanup_stale_tmp_objects`, `cleanup_deleted_objects`, `cleanup_deleted_objects_loop`, `move_to_trash`, and recursive `delete_file`. Deletions normally move paths into `.rustfs.sys/tmp/.trash` using generated UUID names, with disk-full fallback to direct removal.

The `DiskAPI for LocalDisk` implementation supplies all local disk behavior: volume management, object metadata reads/writes, version deletion, data rename, part rename, part checks, raw file reads/writes, directory listing/walking, multi-file reads, disk info, and scan lifecycle.

## Control flow
Startup first canonicalizes or resolves the endpoint path, creates required data-usage state, optionally renames `.rustfs.sys/tmp` to `.rustfs.sys/tmp-old/<uuid>`, recreates `.rustfs.sys/tmp/.trash`, and asynchronously removes the old tmp root. It then reads `.rustfs.sys/format.json`. If format bytes exist, `FormatV3` is decoded and the disk UUID must match the endpoint set/disk indexes. The constructor records disk capacity/static metadata, creates meta volumes, and launches a cleanup loop whose first tick is delayed by `DELETED_OBJECTS_CLEANUP_INTERVAL`.

Read flows start by resolving a bucket/object path and checking volume access unless the path is in internal metadata buckets. `read_version` reads `xl.meta`, converts it into `FileInfo`, and optionally inlines data. Small single-part objects under `DEFAULT_INLINE_BLOCK` may have the shard loaded from `part.N`; missing shard paths cause fallback to metadata-only inline representation. `read_file_stream` and `read_file_zero_copy` validate `offset + length` overflow and file bounds before seeking or mmaping.

Write flows resolve and validate paths, create missing parents under a skip-parent boundary, then write either asynchronously or through `spawn_blocking` for owned `Bytes`. Metadata writes append or replace versions in `FileMeta` and persist `xl.meta`; `write_all_meta` stages bytes under `.rustfs.sys/tmp/<uuid>` then renames to the destination. The `sync` parameter is deliberately ignored by `write_all_internal`, preserving the current durability contract without fsync.

Rename flows distinguish plain files, part files, directory markers, inline object metadata, and non-inline erasure data. `rename_part` enforces source/destination directory-vs-file compatibility, renames the part, writes a sidecar `.meta`, and prunes empty source parents. `rename_file` is the simpler generic path rename. `rename_data` merges the incoming `FileInfo` into destination `xl.meta`; for non-inline data it writes metadata at the source, renames the data directory, then renames `xl.meta`, with cleanup on failure. For inline data it performs read/merge/write/rename in one blocking task.

Deletion flows load `FileMeta`, remove targeted versions, move unshared data directories to trash, rewrite `xl.meta` if versions remain, or remove the metadata path when no versions remain. Batch deletion loops over `FileInfoVersions`. Generic deletes and path deletes also move targets to trash and recursively prune empty parent directories while refusing to operate on filesystem roots or paths outside the volume root.

Namespace walking waits for startup cleanup, emits explicit directory objects when present, lists directories recursively, filters by prefix and `forward_to`, reads `xl.meta` entries into `MetaCacheEntry`, tracks object counts for limits, deduplicates explicit directory markers with real directories, skips multipart data directories discovered from metadata, and writes results through `MetacacheWriter`.

Verification flows either stat each erasure part (`check_parts`) or run full bitrot verification (`verify_file`). `bitrot_verify` retries only the known "bitrot shard file size mismatch" error for an environment-controlled count/delay before converting errors into `CHECK_PART_*` status integers.

## State and persistence behavior
Persistent on-disk state is rooted at the endpoint path. Buckets are directories, objects are directories containing `xl.meta`, non-inline erasure data lives under object data-dir UUIDs with `part.N` files, multipart/internal state lives under `.rustfs.sys`, and deleted/stale paths are moved into `.rustfs.sys/tmp/.trash` for asynchronous cleanup. `format.json` stores the disk identity and erasure set membership; `LocalDisk` caches it but invalidates the cache when the file disappears or changes.

The cleanup state is partially asynchronous. Startup cleanup can continue after construction, and `walk_dir` waits up to `STARTUP_CLEANUP_WAIT_TIMEOUT` for the latch before scanning. Background cleanup runs every five minutes after an initial delay and removes trash entries plus temp directories older than one day.

The disk-info cache updates at most once per second and records capacity, inode counts, filesystem type, root-disk detection, physical device ids, and disk id. `start_scan` increments an atomic counter and `ScanGuard::drop` decrements it, exposing scanner activity in `DiskInfo`.

## Dependencies and integration points
This module depends on the broader `disk` contract (`DiskAPI`, `DiskInfo`, options/response structs, error conversion, filesystem helpers, OS helpers, and constants), `endpoint::Endpoint`, `format::FormatV3`, `rustfs_filemeta` metadata encoding/decoding, erasure bitrot verification, data-usage layout initialization, RustFS global root-disk thresholds, `rustfs_utils` path/OS helpers, `bytes`, `tokio`, `parking_lot`, `metrics`, `tracing`, `uuid`, and platform-specific `libc`, `memmap2`, and `rustix` calls.

The implementation is consumed through `disk/mod.rs` and `disk_store::LocalDiskWrapper`, while remote peers use the same trait shape through RPC. It integrates with bucket scanners through `MetacacheWriter`, with healing/check code through `check_parts` and `verify_file`, with lifecycle/delete code through version deletion, and with startup/format loading through `get_disk_id`.

## Risks and edge cases
Path confinement relies on lexical normalization before `starts_with(root)`. That is fast but should remain sensitive to symlinks, Windows prefixes, and cache entries that are not revalidated against changing filesystem topology. The cache eviction policy is simple and does not check path validity in `get_object_paths_batch`.

Durability may be weaker than callers expect because `write_all_internal` ignores `sync`; atomicity depends primarily on temp-write-plus-rename where used, and direct writes elsewhere can leave partial files if the process exits mid-write. Rename flows are multi-step and have best-effort rollback/cleanup, so crash consistency around object overwrite and old data-dir restoration is a key risk area.

Delete behavior intentionally moves most data to trash and later removes it. Disk-full fallback switches to direct deletion. Background cleanup failures are logged but not escalated, so trash growth or stale temp directories can accumulate if permissions or filesystem errors persist.

`read_file_zero_copy` is described as zero-copy but currently copies mmap contents into `Bytes` for safe ownership. That avoids unsafe lifetime hazards but affects performance expectations. Offset arithmetic overflow is guarded in both stream and mmap reads.

Volume-name validation is minimal on non-Windows platforms and allows names containing slashes/colons in tests, so higher layers must enforce S3 bucket rules. Access checks are skipped for internal metadata prefixes, which is necessary for system maintenance but expands the trusted surface.

## Test signals
The in-file tests cover format-id cache invalidation after `format.json` removal, startup temp cleanup and trash recreation, stale tmp movement, cleanup interval not ticking immediately, cleanup barrier notification and timeout, recursive scan inclusion and deduplication, `forward_to` behavior with repeated prefixes, hidden delete marker limit accounting, multipart data-dir filtering in walks, basic volume/file operations, disk info shape, read offset overflow rejection, volume-name validation, helper file reads/metadata reads, root-path and lexical normalization behavior, file-cache reclaim threshold environment handling, and bitrot size-mismatch string classification.
