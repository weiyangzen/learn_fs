# sources/user-network-fs/samba/source3/modules/vfs_default.c

## Purpose
`vfs_default.c` is Samba's terminal VFS implementation. It supplies concrete behavior for every VFS hook using POSIX/syscall wrappers plus Samba path, security, DFS, ACL, xattr, async, durable-handle, offload-copy, and FSCTL semantics.

## Important APIs, Types, And Functions
`vfs_default_fns` is the complete `struct vfs_fn_pointers`; `vfs_default_init()` asserts all functions are present before registration. Major areas include connect/open hardening with proc-fd and `openat2()` resolve flags, disk/quota/statvfs/capability hooks, DFS referral create/read/get, directory wrappers, sync and async pread/pwrite/fsync, metadata operations, locks/leases, file-id creation, stream info, FSCTL dispatch, DOS xattr attributes, server-side copy/offload, NT and POSIX ACLs, xattrs, and durable handle helpers.

## Control Flow
Most hooks profile, validate stream/pathref assumptions, call a POSIX or Samba helper, and return errno/NTSTATUS in VFS form. `vfswrap_openat()` uses `openat2()` for no-symlink/no-xdev resolution and falls back when unsupported. Async I/O schedules pthreadpool jobs and falls back to synchronous work on `EAGAIN`. FSCTL handling delegates shadow-copy enumeration to `SMB_VFS_GET_SHADOW_COPY_DATA()`, which is how modules such as Ceph snapshots surface Previous Versions. Server-side copy validates tokens, locks, offsets, and handles, tries reflink or `copy_file_range()`, then falls back to an async read/write loop.

## State And Persistence
Most persistent state lives in the filesystem, xattrs, ACLs, reparse metadata, durable cookies, or Samba databases. Process-level state includes a one-time ioctl log flag, the offload token context, and a static `try_copy_file_range` fast-path switch. Async request state is talloc-owned and protected from unsafe cancellation while worker threads may reference it.

## Dependencies And Integration Points
The file integrates with loadparm, profiling, DFS helpers, security descriptors, POSIX ACL mapping, DMAPI, pthreadpool/tevent, strict locks, offload-token DB, durable handle code, reparse point helpers, xattr DOS attributes, and platform syscall wrappers. Every higher module that calls `SMB_VFS_NEXT_*` ultimately relies on these defaults.

## Risks
As the terminal module, errno mapping and hook coverage errors are broad blast-radius bugs. Some behavior is intentionally approximate: allocated ranges, find-files-by-SID, default streams, and compression. Pathref operations may degrade to path-based fallbacks without proc-fds. Async xattr depends on per-thread credentials. The `try_copy_file_range` switch is process-wide after unsupported errors.

## Test Signals
Test complete hook registration, `openat2()` success and fallback, pathref chmod/chown/xattrs with and without proc-fds, async I/O fallback, DFS symlink parsing, FSCTL shadow-copy marshalling, strict allocation truncate, server-side copy fast/fallback paths, DOS xattr parsing and root retry, durable reconnect, ACL wrappers, and errno preservation.
