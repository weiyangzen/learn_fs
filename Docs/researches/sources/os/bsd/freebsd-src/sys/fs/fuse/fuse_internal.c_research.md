# File Research: sources/os/bsd/freebsd-src/sys/fs/fuse/fuse_internal.c

This file implements shared FUSE vnode/VFS helper operations used by vnode ops, VFS ops, I/O, and device IPC paths. It is the main translation layer between FreeBSD vnode semantics and FUSE protocol requests.

Key responsibilities:
- Tracks lookup-cache statistics with `fuse_lookup_cache_hits` and `fuse_lookup_cache_misses`.
- Resolves cached vnodes by FUSE node id through `vfs_hash_get`, while enforcing `entry_cache_timeout`.
- Implements permission checking in `fuse_internal_access`.
  - Enforces read-only mount behavior for mutable access.
  - Restricts access to the mount owner unless `FSESS_DAEMON_CAN_SPY` is set.
  - Uses local `vaccess` when `FSESS_DEFAULT_PERMISSIONS` is active.
  - Sends `FUSE_ACCESS` unless the daemon is known not to implement it.
- Converts and caches `struct fuse_attr` into FreeBSD `struct vattr` in `fuse_internal_cache_attrs`.
  - Maintains vnode size through `fuse_vnode_setsize`.
  - Warns once per mount on cache incoherency and writeback-cache incoherency.
  - Honors zero TTL by returning attributes without installing them in the vnode cache.
- Implements `FUSE_FSYNC` / `FUSE_FSYNCDIR` dispatch for every open file handle on a vnode.
  - Supports synchronous wait and asynchronous callback modes.
  - Caches `ENOSYS` as not implemented.
- Handles daemon asynchronous invalidation notifications.
  - `fuse_internal_invalidate_entry` reads `fuse_notify_inval_entry_out`, locates the parent vnode, invalidates a namecache entry, and clears parent attrs.
  - `fuse_internal_invalidate_inode` reads `fuse_notify_inval_inode_out`, locates the vnode, invalidates buffers if the notification has an offset, and clears attrs.
- Implements creation/remove/rename helpers.
  - `fuse_internal_mknod` builds ABI-sensitive `fuse_mknod_in`.
  - `fuse_internal_newentry*` builds creation requests, validates `fuse_entry_out`, instantiates vnodes, sends `FORGET` if vnode creation fails, clears parent attrs, and caches returned attrs.
  - `fuse_internal_remove` sends `UNLINK`/`RMDIR`, adjusts cached link count, clears parent attrs, and marks disappearing vnodes revoked.
  - `fuse_internal_rename` sends old/new names in the `FUSE_RENAME` payload.
- Implements directory reading.
  - `fuse_internal_readdir` loops over `FUSE_READDIR`.
  - `fuse_internal_readdir_processdata` converts packed `fuse_dirent` records into native `dirent`, updates directory offsets, and fills optional NFS cookies.
- Implements lookup lifetime release.
  - `fuse_internal_forget_send` sends noreply `FUSE_FORGET`.
  - `fuse_internal_forget_callback` chains a follow-up forget from a ticket.
- Implements attribute fetch and setattr.
  - `fuse_internal_do_getattr` sends `FUSE_GETATTR`, overlays dirty local size/timestamps before caching, and revokes stale type-changing vnodes.
  - `fuse_internal_getattr` returns cached attrs when valid, otherwise fetches from daemon.
  - `fuse_internal_setattr` builds `fuse_setattr_in`, supports uid/gid/size/time/mode/ctime, uses a write file handle when truncating if available, clears dirty size/timestamps on success, and caches returned attrs.
- Implements `fuse_internal_send_init` and `fuse_internal_init_callback`.
  - Sends kernel ABI `7.35`.
  - Advertises supported capabilities including async read, POSIX locks, export support, big writes, ioctl-dir, writeback cache, no-open/no-opendir support, and setxattr extension.
  - Parses daemon `fuse_init_out`, selects max write/read-ahead/time granularity/cache mode, and marks unsupported operations based on protocol version.
- Implements SUID/SGID clearing on write for default-permission mounts via root-credential `SETATTR`.

Integration points:
- Uses `fuse_dispatcher` and tickets from `fuse_ipc.c`.
- Uses vnode state, attr-cache locks, size helpers, and dirty flags from `fuse_node.c` / `fuse_node.h`.
- Uses direct buffer invalidation via `fuse_io_invalbuf`.
- Uses file-handle lookup from `fuse_file.h`.
- Provides common helpers consumed by vnode operations outside this group.

Notable risks and research hooks:
- Cache coherency depends heavily on daemon TTL behavior and `FSESS_*` warnings are once-per-session, not hard failures except for some protocol violations.
- Invalidation notifications cannot validate generation numbers, so they may invalidate a reused inode/name unnecessarily.
- `fuse_internal_setattr` can send root credentials when `cred == NULL`; callers must ensure that path is intentional.
- `fuse_internal_readdir_processdata` treats malformed partial/oversized directory entries as end-of-directory or `EINVAL`, making daemon correctness important for directory iteration.
- Writeback cache is explicitly warned as unsafe with incoherent servers.
