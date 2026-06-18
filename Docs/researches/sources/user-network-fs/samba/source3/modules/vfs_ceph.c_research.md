# sources/user-network-fs/samba/source3/modules/vfs_ceph.c

## Purpose
`vfs_ceph.c` is the legacy Samba VFS backend for CephFS via the userspace `libcephfs` client. It replaces ordinary POSIX filesystem calls with libcephfs calls, supports shared libcephfs mount instances across connections with identical configuration, exposes stat/xattr/DFS/POSIX ACL behavior, and adapts Ceph's `-errno` return convention to Samba's `errno`/`-1` convention.

## Important APIs, types, and functions
- `status_code()` and `lstatus_code()` convert negative Ceph errors into Samba-style returns.
- `struct cephmount_cached` tracks a mount cookie, refcount, `ceph_mount_info *`, and DLIST links.
- `cephmount_get_cookie()` keys mounts by `ceph:config_file`, `ceph:user_id`, and `ceph:filesystem`.
- `cephmount_mount_fs()` creates a Ceph mount, reads config, enables `client_acl_type=posix_acl`, disables local default permission checks with `fuse_default_permissions=false`, optionally selects a filesystem, and mounts.
- `cephwrap_connect()`/`cephwrap_disconnect()` manage mount-cache references and store the mount in `handle->data`.
- Directory/file wrappers cover statfs, fdopendir/readdir/closedir, mkdir/open/close/pread/pwrite/lseek/rename/fsync/stat/fstat/fstatat/lstat/timestamps/unlink/chmod/chown/chdir/truncate/fallocate/links/mknod/realpath.
- `init_stat_ex_from_ceph_statx()` maps `ceph_statx` into Samba `stat_ex`, including btime.
- DFS wrappers store referrals as `msdfs:` symlinks and parse them on read.
- Xattr and DOS attribute wrappers integrate with Samba EA DOS attributes while preserving btime from Ceph statx.
- POSIX ACL hooks use `posixacl_xattr_*` helpers.

## Control flow
Connection setup first attempts to reuse a cached mount for the share's cookie. If none exists, it mounts a new CephFS client and inserts it into the cache. Each VFS operation then calls the corresponding libcephfs API using `handle->data`. Many operations are fd-relative (`ceph_openat`, `ceph_mkdirat`, `ceph_unlinkat`), while rename/link/mknod build full paths before calling path-based APIs. The module rejects named streams for path operations by returning `ENOENT`.

Async read/write/fsync are "fake async": the send function performs the synchronous libcephfs call immediately, stores the result in a tevent request, and posts completion. `sendfile` and `recvfile` return `ENOTSUP` because libcephfs is userspace. Strict allocation uses `ceph_fallocate()` when growing files. Filesystem sharemode is not implemented and warns operators to consider `kernel share modes = no`.

## State and persistence behavior
Persistent state is entirely in CephFS: files, directories, xattrs, ACL xattrs, timestamps, symlinks, and DFS referral symlinks. In-process state consists of the global mount cache and per-handle `handle->data` mount pointer. Mount cache entries persist until their refcount reaches zero at disconnect, then unmount and release the Ceph client.

## Dependencies and integration points
The module depends directly on `cephfs/libcephfs.h`, Samba VFS, statvfs/statx translation, tevent, smbd profiling hooks, POSIX ACL xattr helpers, DFS referral helpers, and loadparm. It is registered in `wscript_build` as `vfs_ceph` with Ceph library dependencies.

## Risks and edge cases
- The global mount cache is not visibly synchronized in this file; concurrent connect/disconnect behavior depends on smbd process/thread assumptions.
- Fake async can block the event loop during large Ceph reads/writes/fsyncs.
- `realpath()` is a string join and explicitly does not resolve symlinks.
- Sharemode/locking support is minimal: lock succeeds, getlock returns false, and filesystem sharemodes are unsupported.
- Named streams are largely treated as missing, so stream support must come from other modules if needed.
- Error handling must consistently convert `-errno`; missed conversions would invert or lose failures.

## Test signals
No direct tests were found in the inspected subset. Validation requires a CephFS test cluster: mount reuse across shares with identical cookies, basic filesystem operations, stat btime preservation, xattr/DOS attribute round trips, DFS symlink referrals, strict allocation, fake async behavior, and unsupported sendfile/sharemode paths. Build registration in `wscript_build` is the static integration signal.
