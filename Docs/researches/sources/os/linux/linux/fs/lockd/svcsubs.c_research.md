# File Research: sources/os/linux/linux/fs/lockd/svcsubs.c

## Purpose
`svcsubs.c` contains support routines for the lockd server: an `nlm_file` hash table keyed by NFS file handle, file open/close/refcount handling, lock/share/block traversal, host resource cleanup, and exported helpers for unlocking lockd state by superblock or server IP address.

## Main Responsibilities
- Maintains a 128-bucket global `nlm_files` hash table protected by `nlm_file_mutex`.
- Maps lock type to open mode via `lock_to_openmode()`.
- Opens files through `nlmsvc_ops->fopen()` in `nlm_do_fopen()`, supporting read, write, or either mode.
- Looks up or creates `nlm_file` objects in `nlm_lookup_file()`.
- Deletes `nlm_file` objects when refcounts and all associated locks/blocks/shares are gone.
- Traverses VFS POSIX locks with lockd lock-manager operations to remove resources matching a host predicate.
- Traverses all files for garbage collection/resource invalidation and optional filtering.
- Exports `nlmsvc_unlock_all_by_sb()` and `nlmsvc_unlock_all_by_ip()`.

## Key Functions
- `file_hash()`: hashes the NFSv2-sized file handle bytes into `nlm_files`.
- `nlm_do_fopen()`: opens missing read/write file pointers and maps filesystem errors to internal lockd statuses.
- `nlm_lookup_file()`: finds an existing file object or allocates a new one, initializes mutex/list/block state, opens required file mode, and increments `f_count`.
- `nlm_release_file()`: decrements `f_count`, inspects remaining VFS locks/shares/blocks, and deletes the file object if unused.
- `nlm_traverse_locks()`: walks `flc_posix` locks on the inode, finds lockd-owned locks, and unlocks matching host resources.
- `nlm_traverse_files()`: walks the hash table safely while temporarily incrementing file refs and dropping the global mutex during expensive per-file inspection.
- `nlmsvc_mark_resources()`: marks hosts still holding resources.
- `nlmsvc_free_host_resources()`: removes all locks, blocked locks, and shares for one host.
- `nlmsvc_invalidate_all()`: removes all locks held for NFS clients.

## Integration Points
- Depends on `nlmsvc_ops` for filesystem-specific file handle open/close.
- Uses VFS lock contexts from `fs/locks.c` to find and remove lockd POSIX locks.
- Calls `nlmsvc_traverse_blocks()` from `svclock.c` and `nlmsvc_traverse_shares()` from `svcshare.c`.
- Used by service shutdown, host reboot handling, FREE_ALL, unexport/unmount cleanup, and IP-based resource cleanup.

## Concurrency and Lifetime Notes
- `nlm_file_mutex` protects the file hash and `f_count`.
- Each `nlm_file` also has `f_mutex` for per-file operations.
- Traversal increments `f_count`, drops `nlm_file_mutex`, inspects/removes resources, then reacquires and potentially deletes the file.
- Because `fs/locks.c` can split/merge/delete locks without lockd-specific notifications, `nlm_file_inuse()` must inspect the inode's lock context rather than relying only on lockd's own counters.

## Risks and Edge Cases
- `nlm_do_fopen()` maps `-EWOULDBLOCK` to `nlm__int__drop_reply`, allowing RPC deferral semantics.
- `nlmsvc_free_host_resources()` calls `BUG()` if matching locks cannot be removed, treating cleanup failure as fatal.
- File handle hashing only uses `NFS2_FHSIZE` bytes, while other paths can carry larger file handles; this mirrors historical lockd behavior for this table.
