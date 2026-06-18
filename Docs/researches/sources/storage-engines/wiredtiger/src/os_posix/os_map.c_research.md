<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_map.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_map.c

## Purpose
Implements explicit POSIX memory-map operations exposed through file handles for block-manager read paths and mapped-file optimizations.

## Important APIs, Types, and Functions
`__wti_posix_map`, `__wti_posix_unmap`, and, when `HAVE_POSIX_MADVISE` is available, `__wti_posix_map_preload` and `__wti_posix_map_discard`.

## Control Flow
`__wti_posix_map` gets current file size from `fh_size`, calls `mmap` using handle protection/flags, and returns region plus length. Preload/discard align addresses down to connection page size before issuing `posix_madvise`. Preload expands sequential scan hints for `WT_SESSION_READ_WONT_NEED`. Unmap logs and calls `munmap`.

## State and Persistence Behavior
No WiredTiger metadata is persisted. Mapped bytes reflect the backing file. The caller must ensure the underlying file does not change inconsistently while mapped; this layer intentionally has no locking.

## Dependencies and Integration Points
Installed by `os_fs.c` as `fh_map`/`fh_unmap` and optional `fh_map_preload`/`fh_map_discard`. It relies on `WT_FILE_HANDLE_POSIX`, connection page size, block manager map bounds, and POSIX mmap/madvise.

## Risks and Edge Cases
Mapping zero-length files and files that resize underneath the caller are caller responsibilities. Alignment math affects madvise correctness. `MAP_NOCORE` is conditional and platform-specific.

## Test Signals
Mapped reads, scan-preload behavior, discard calls, zero-length/error paths, and map/unmap leak checks are relevant signals.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_map.c -->
