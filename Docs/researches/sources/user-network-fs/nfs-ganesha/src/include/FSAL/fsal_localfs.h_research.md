<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h -->
# sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h

## Purpose
`FSAL/fsal_localfs.h` declares common support for FSALs that map onto local POSIX filesystems. It tracks discovered filesystems, relationships between filesystems and exports, claims, FSID/device indexes, and cleanup/reindex operations. When local filesystem hosting is unavailable, it provides no-op stubs.

## Important APIs, types, and functions
- Under `!GSH_CAN_HOST_LOCAL_FS`, `release_posix_file_systems()` and optional `dbus_cache_init()` are no-op inline stubs and `struct fsal_filesystem` is forward-declared.
- `struct fsal_filesystem` describes one filesystem: tree/list links, parent/children, owning FSAL, export list, private data, path/device/type, claim callbacks, path/name lengths, AVL nodes for FSID and device indexes, FSID/device values, claim counters, and verifier truncation policy.
- `struct fsal_filesystem_export_map` links a filesystem to an export, supports child maps, and records claim type.
- Core APIs include `populate_posix_file_systems()`, `resolve_posix_filesystem()`, `claim_posix_filesystems()`, `release_posix_file_systems()`, `release_posix_file_system()`, `unclaim_all_export_maps()`, and `get_fs_first_export_ref()`.
- Lookup/reindex APIs include `lookup_fsid_locked()`, `lookup_dev_locked()`, `lookup_fsid()`, `lookup_dev()`, `re_index_fs_fsid()`, `re_index_fs_dev()`, and `change_fsid_type()`.
- `fsal_fs_compare_fsid()` compares FSID type, major, and optionally minor fields.
- `LogFilesystem` formats detailed filesystem topology, export, private data, and claim counters for debug logging.
- `open_dir_by_path_walk()` safely opens a path by walking from a starting directory fd.

## Control flow
Local-FS capable builds populate filesystem records from POSIX paths, resolve which filesystem owns an export path, claim filesystem subtrees for exports, and index filesystems by FSID and device. Export teardown unclaims maps and can release filesystems when no claims remain. Lookup helpers use `fs_lock` externally or internally depending on the locked variant.

## State and persistence
The file declares shared in-memory filesystem topology and indexes protected by external `fs_lock`. It mirrors persistent mounted filesystem facts such as path, device, type, FSID, name length, and statfs-derived attributes. Claim counters record active export relationships and must be balanced during export load/unload.

## Dependencies and integration points
It depends on `fsal_api.h`, AVL trees, Ganesha export/module types, FSAL claim callbacks, DBus optional cache initialization, and POSIX stat/open concepts. It integrates local FSAL modules, export management, FSID/device lookup used by file-handle decoding, and verifier behavior for filesystems with truncated timestamps.

## Risks
- Many-to-many export/filesystem maps and claim counters are easy to leak or unbalance, especially during partial export-load failure.
- Reindexing FSID or device while lookups run requires correct `fs_lock` use.
- `fsal_fs_compare_fsid()` ignores minors for `FSID_MAJOR_64`, so callers must supply consistent types.
- No-op stubs under `!GSH_CAN_HOST_LOCAL_FS` can hide missing feature coverage until runtime configuration asks for local FS behavior.
- Path walking must handle symlinks, races, and permission errors in implementation.

## Test signals
- Local-FS integration tests should claim and unclaim exports rooted at filesystem roots, subtrees, children, and overlapping paths.
- Lookup tests should resolve by FSID and device before and after reindex operations.
- Failure-injection tests should abort export load mid-claim and verify all maps and counters are unwound.
- Builds with `GSH_CAN_HOST_LOCAL_FS` enabled and disabled should compile and run expected stubs or real paths.
- DBus builds should validate filesystem cache initialization and reporting if implemented.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/include/FSAL/fsal_localfs.h -->
