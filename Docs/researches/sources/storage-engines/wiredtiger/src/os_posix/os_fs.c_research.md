<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fs.c -->
# sources/storage-engines/wiredtiger/src/os_posix/os_fs.c

## Purpose
Implements WiredTiger's default POSIX `WT_FILE_SYSTEM` and POSIX `WT_FILE_HANDLE` methods: existence, open, remove, rename, size/free-space, read/write, sync, truncate/extend, file locking, and optional mmap-backed file I/O.

## Important APIs, Types, and Functions
`__wt_os_posix` builds the file-system jump table. `WT_FILE_HANDLE_POSIX` carries the fd plus mmap state. `__posix_open_file`, `__posix_file_read`, `__posix_file_write`, `__posix_file_sync`, `__posix_file_truncate`, `__posix_fs_remove`, and `__posix_fs_rename` implement the main operations. `__wti_posix_prepare_remap_resize_file`, `__wti_posix_release_without_remap`, and `__wti_posix_remap_resize_file` coordinate mmap resize.

## Control Flow
Open translates WiredTiger flags to POSIX `open` flags, applies close-on-exec, optional `O_DSYNC` for logs, fadvise hints, durable directory sync, and installs handle methods. Reads/writes are chunked at 1GB. If connection-wide mmap I/O is enabled, file I/O first tries mapped memory and falls back to syscalls. Truncate prepares mmap remap, calls `ftruncate`, and either remaps or releases the resize flag. Durable remove/rename sync backing directories on Linux.

## State and Persistence Behavior
The layer treats sync failure as fatal/panic rather than retryable. `WT_DISAGG_NO_SYNC` can suppress flushes. Linux durable operations fsync containing directories. mmap I/O protects mapped buffers with `mmap_resizing` and `mmap_usecount`, preventing remap while readers/writers copy from a mapping.

## Dependencies and Integration Points
Depends on POSIX syscalls, `statvfs`, `posix_fadvise`, `sync_file_range`, mmap, WiredTiger stats, verbosity, block-manager file handles, log manager sync configuration, and `os_dir.c` directory-list hooks.

## Risks and Edge Cases
fdatasync/fsync errors panic; tests should include fault injection. `O_NOATIME`, `F_FULLFSYNC`, `sync_file_range`, and directory fsync vary by platform. mmap remap races are subtle, especially when writes extend files. Read/write stat increments happen after length is consumed, so instrumentation should be checked carefully if changed.

## Test Signals
Useful signals are crash-recovery tests around durable create/remove/rename, direct syscall fault tests, mmap-all stress with concurrent file growth/truncation, lock-open conflict tests, and platform matrix coverage for fadvise and sync variants.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/src/os_posix/os_fs.c -->
