# File Research: sources/teaching/minix/minix/servers/vfs/stadir.c

## Purpose
Implements VFS system calls for directory context changes and file system status queries: `fchdir`, `chdir`, `chroot`, `stat`, `fstat`, `lstat`, `statvfs1`, `fstatvfs1`, and `getvfsstat`.

## Main Entry Points
- `do_fchdir()` changes `fp->fp_wd` to an already-open file descriptor vnode.
- `do_chdir()` resolves a pathname and changes current working directory.
- `do_chroot()` resolves a pathname and changes root directory; requires `super_user`.
- `do_stat()`, `do_lstat()`, `do_fstat()` forward inode stat requests to the owning FS via `req_stat`.
- `update_statvfs()` refreshes a mount's cached `statvfs` fields from the file server.
- `do_statvfs()`, `do_fstatvfs()` expose mount statistics for a path or fd.
- `do_getvfsstat()` enumerates reportable mounted file systems.

## Control Flow and State
Path-based calls use `fetch_name` or `copy_path`, initialize `struct lookup`, set vmnt/vnode lock requirements, call `eat_path`, perform the operation, then unlock and `put_vnode`. `change_into()` validates that the target vnode is a searchable directory before replacing either `fp_wd` or `fp_rd`.

`fill_statvfs()` either refreshes statistics unless `ST_NOWAIT` is set or uses `vmp->m_stats`; then it overlays VFS-local metadata such as read-only state, fsid, mount path, mount source, and filesystem type before copying to userspace with `sys_datacopy_wrapper`.

## Dependencies
Depends on VFS pathname resolution (`path.h`), filp lookup (`file.h`), vnode/vmnt locks, FS request helpers such as `req_stat` and `req_statvfs`, and MINIX message fields in `job_m_in`.

## Concurrency and Locking
The file consistently takes `VMNT_READ` and `VNODE_READ` locks around resolved path targets. `do_getvfsstat()` intentionally avoids vmnt locking for `ST_NOWAIT` and relies on `VMNT_CANSTAT` to skip transient mounts; it locks only when it may query file servers.

## Risks and Notes
`do_getvfsstat()` skips mounts being mounted/unmounted and PFS. `fill_statvfs()` maps any refresh failure to `EIO`. `change_into()` correctly handles identity replacement by returning early when the target vnode is already the stored directory.
