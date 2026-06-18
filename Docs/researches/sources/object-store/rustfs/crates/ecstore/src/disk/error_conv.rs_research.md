# sources/object-store/rustfs/crates/ecstore/src/disk/error_conv.rs

## Purpose
`error_conv.rs` translates generic `std::io::Error` values from filesystem operations into disk-layer semantic errors. It provides context-specific mappings for file, volume, whole-disk, access-check, and unformatted-disk paths while still returning `std::io::Error` so callers can use existing `map_err` flows and later recover `DiskError` via downcast.

## Important APIs, Types, And Functions
- `to_file_error` maps file-level errors to object/file semantics: `NotFound` to `FileNotFound`, permission and path-shape problems to `FileAccessDenied` or `IsNotRegular`, `UnexpectedEof` to `FaultyDisk`, invalid data to `FileCorrupt`, and storage-full to `DiskFull`.
- `to_volume_error` maps volume/bucket operations, converting not-found to `VolumeNotFound`, permission to `DiskAccessDenied`, directory-not-empty to `VolumeNotEmpty`, and embedded file errors to volume equivalents.
- `to_disk_error` maps disk-root access, converting not-found or embedded file/volume not-found to `DiskNotFound`, and access failures to `DiskAccessDenied`.
- `to_access_error` maps filesystem access checks to a caller-supplied permission error while preserving volume-not-found and faulty-disk signals.
- `to_unformatted_disk_error` is used while probing `format.json`; most absence, EOF, invalid data, or unknown errors become `UnformattedDisk`, but access denied remains `DiskAccessDenied`.

## Control Flow
Each function first matches the outer `io::ErrorKind`. For `Other`, it attempts to downcast the `io::Error` into `DiskError`. If downcast succeeds, selected variants are remapped according to the context; otherwise the embedded disk error passes through or falls back to the next broader converter. If downcast fails, conversion usually delegates downward (`disk` to `volume` to `file`) or, for unformatted probing, collapses to `UnformattedDisk`.

This layered flow allows local disk code to call `map_err(to_file_error)` or `map_err(to_volume_error)` close to the filesystem operation, while preserving higher-level operation semantics. For example, a raw `NotFound` during `stat_volume` should report `VolumeNotFound`, not `FileNotFound`.

## State And Persistence Behavior
This file is stateless and has no persistence. Its behavior affects durable control flow indirectly: during startup, `to_unformatted_disk_error` determines whether a disk is treated as unformatted and eligible for format creation or migration; during deletes and writes, `DiskFull`, access-denied, or volume-not-empty mappings influence quorum decisions and healing.

## Dependencies And Integration Points
The module depends only on `DiskError`. It is heavily used by `disk/local.rs` around format loading, metadata reads/writes, file opens, renames, deletes, volume creation/listing/stat, path access, and data part handling. `disk/os.rs` also uses `to_file_error` for OS disk checks. The converted errors then flow into `error_reduce.rs`, `disk_store.rs`, store initialization, and remote error transport.

## Risks And Edge Cases
- The converters return `std::io::Error`, not `DiskError`, so callers must consistently use `.into()` or `DiskError::from` later. A missed conversion can leave a generic I/O error at higher layers.
- Some mappings are intentionally broad, such as `InvalidInput` to `FileNotFound` and `UnexpectedEof` to `FaultyDisk`; this may hide malformed-path versus missing-file distinctions.
- `to_unformatted_disk_error` collapses most errors to `UnformattedDisk`, which is useful for init but risky if used outside format probing.
- Platform-specific `ErrorKind` variants such as `TooManyLinks` and `StorageFull` are guarded in tests but may behave differently across OSes.

## Test Signals
Tests cover all basic mappings for file, volume, disk, access, and unformatted contexts; embedded `DiskError` remapping through `ErrorKind::Other`; fallback delegation; passthrough of unknown interrupted errors where appropriate; no-recursion behavior for unformatted conversion; conversion chains such as file-not-found to volume-not-found; and Unix-specific error kinds for too many links and storage full.
