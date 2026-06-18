# sources/object-store/rustfs/crates/ecstore/src/disk/mod.rs

## Purpose
This file defines the public disk subsystem boundary for `ecstore`. It declares disk-related submodules, shared constants for RustFS metadata paths and file names, the local-or-remote `Disk` enum, the `DiskAPI` trait that storage code uses, and the request/response/options structs shared across local disk, remote disk, RPC, healing, scanning, and metadata paths.

## Important APIs, types, and functions
The module exports metadata constants such as `RUSTFS_META_BUCKET`, `RUSTFS_META_MULTIPART_BUCKET`, `RUSTFS_META_TMP_BUCKET`, `RUSTFS_META_TMP_DELETED_BUCKET`, `BUCKET_META_PREFIX`, `FORMAT_CONFIG_FILE`, `STORAGE_FORMAT_FILE`, and `STORAGE_FORMAT_FILE_BACKUP`.

`DiskStore` is `Arc<Disk>`. `FileReader` and `FileWriter` are boxed async read/write trait objects. `Disk` has `Local(Box<LocalDiskWrapper>)` and `Remote(Box<RemoteDisk>)` variants, giving one enum type for both local filesystem disks and RPC-backed peer disks.

`DiskAPI` is the core async trait. It covers identity and health (`to_string`, `is_online`, `is_local`, `host_name`, `endpoint`, `close`, `get_disk_id`, `set_disk_id`, `path`, `get_disk_location`), volume operations, metadata operations (`write_metadata`, `update_metadata`, `read_version`, `read_xl`, `read_metadata`, `rename_data`, version deletes), file operations (`read_file`, stream/zero-copy reads, append/create/rename, `rename_part`, generic delete), verification (`verify_file`, `check_parts`, `read_parts`), bulk reads, raw read/write-all, disk info, and scan guard creation.

`new_disk` selects the implementation from `Endpoint::is_local`: local endpoints instantiate `LocalDisk`, wrap it in `LocalDiskWrapper` with optional health checks, and return `Disk::Local`; remote endpoints build internode data transport from environment and create `RemoteDisk`.

Data structs include `DiskInfo`, `Info`, `FileInfoVersions`, `WalkDirOptions`, `DiskOption`, `RenameDataResp`, `DeleteOptions`, `ReadMultipleReq`, `ReadMultipleResp`, `VolumeInfo`, `ReadOptions`, `UpdateMetadataOpts`, `CheckPartsResp`, and `DiskLocation`. Constants and helpers for part verification are `CHECK_PART_UNKNOWN`, `CHECK_PART_SUCCESS`, `CHECK_PART_DISK_NOT_FOUND`, `CHECK_PART_VOLUME_NOT_FOUND`, `CHECK_PART_FILE_NOT_FOUND`, `CHECK_PART_FILE_CORRUPT`, `conv_part_err_to_int`, `has_part_err`, and `count_part_not_success`.

## Control flow
Every `DiskAPI for Disk` method is a dispatch shim: it matches on `Disk::Local` or `Disk::Remote` and forwards the call to the wrapped implementation with the same arguments. Runtime health helpers outside the trait (`runtime_state`, `offline_duration_secs`, `last_capacity_snapshot`, `record_capacity_probe`, `reset_health_for_store_init_retry`, and `enable_health_check`) follow the same delegation model.

`new_disk` is the construction choke point. Local construction stays in-process and canonicalizes/initializes the local disk through `LocalDisk::new`. Remote construction configures the internode data transport before creating `RemoteDisk`, so failures to build transport surface before the disk store enters the pool.

`FileInfoVersions::find_version_index` parses a requested version UUID and searches the `versions` vector for a matching `FileInfo.version_id`; empty input returns `None`. `DiskLocation::valid` requires pool, set, and disk indexes all to be populated. `conv_part_err_to_int` maps selected `DiskError` values and `None` into stable integer status codes, warning and returning `CHECK_PART_UNKNOWN` for anything else.

## State and persistence behavior
This module itself does not persist state. It defines the state contracts carried by implementors. `DiskInfo` is the serialized/call-returned snapshot of capacity, filesystem identity, health flags, endpoint/mount path, physical devices, disk UUID, media type, metrics, and error string. `FileInfoVersions` models the version set and free-version set for one object. `DeleteOptions` carries recursive/immediate/undo-write behavior plus an old data-dir UUID for rollback. `WalkDirOptions` carries scanner cursor and filtering state.

Because the enum delegates to either local or remote implementations, persistence semantics depend on the selected variant: local writes hit filesystem state under a disk root, remote writes cross RPC to a peer. The trait is designed so callers can treat both uniformly.

## Dependencies and integration points
This file ties together `disk_store::LocalDiskWrapper`, `local::LocalDisk`/`ScanGuard`, `rpc::RemoteDisk`, `endpoint::Endpoint`, disk health state, file metadata types, admin `DiskMetrics`, `bytes`, `serde`, `tokio::io`, `time`, and `uuid`. It is the common contract used by erasure sets, healing, object metadata code, scanners, RPC services, and admin info calls.

The status integer constants explicitly warn that changing their order can cause data loss during mixed-version operation, making this module part of the wire/storage compatibility surface.

## Risks and edge cases
The dispatch layer is repetitive; adding a trait method requires updating the trait, the enum implementation, local implementation, remote implementation, and wrapper layers together. Missing or inconsistent delegation would cause local/remote behavior drift.

`find_version_index` uses `Uuid::parse_str(v).unwrap_or_default()`, so malformed UUID strings search for the nil UUID rather than immediately failing. That may be intentional tolerance but can surprise callers if nil version ids are possible.

`DiskInfoOptions` includes `disk_id`, `metrics`, and `noop`, but individual implementations may ignore some fields; callers should not assume every option is honored uniformly.

Part status constants are compatibility-sensitive. Any reordering or reinterpretation risks corrupting healing decisions when nodes run different versions.

## Test signals
The tests validate `DiskLocation::valid`, `FileInfoVersions::find_version_index`, part-error conversion and detection helpers, option/response struct construction, metadata constants, local `new_disk` construction, enum method behavior for local disks, and health-reset delegation for both local and remote variants. The remote delegation test constructs a `RemoteDisk` with `TcpHttpInternodeDataTransport` and checks that runtime state resets to online.
