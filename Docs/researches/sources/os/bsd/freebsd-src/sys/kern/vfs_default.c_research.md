# File Research: sources/os/bsd/freebsd-src/sys/kern/vfs_default.c

## Purpose
Provides FreeBSD's default vnode operation vector and standard VOP/VFS helper implementations. Filesystems inherit these functions when they do not provide specialized operations.

## Main Elements
- Default vnode operation vector:
  - `default_vnodeops` wires common defaults for access, locking, polling, buffer mapping, fsync, paging, stat, inotify, ioctl, file locking, writecount/text handling, copy-file-range, and unsupported operations.
  - Missing operations generally return `EOPNOTSUPP`, `EINVAL`, `ENOTDIR`, or panic where a missing implementation indicates a filesystem bug.
- Generic return/panic stubs:
  - `vop_eopnotsupp()`, `vop_ebadf()`, `vop_enotty()`, `vop_einval()`, `vop_enoent()`, `vop_eagain()`, `vop_null()`, and `vop_panic()`.
  - `vop_nolookup()` reports `ENOTDIR`; `vop_norename()` releases rename arguments and returns unsupported; `vop_nostrategy()` completes the buffer with `BIO_ERROR`.
- Access and locking:
  - `vop_stdaccess()` and `vop_stdaccessx()` convert between classic and extended access masks.
  - `vop_stdlock()`, `vop_stdunlock()`, and `vop_stdislocked()` honor `v_vnlock`.
  - `vop_lock()`, `vop_unlock()`, and `vop_islocked()` are optimized variants for vnodes using their embedded lock.
- Advisory locking:
  - `vop_stdadvlock()`, `vop_stdadvlockasync()`, and `vop_stdadvlockpurge()` delegate to lockf routines, with special handling for `SEEK_END` and local-filesystem exclusive-open atomicity.
- Filesystem and pathname defaults:
  - `vop_stdpathconf()` returns POSIX/default pathconf values.
  - `vop_stdbmap()` maps logical blocks as contiguous offsets in the vnode's own buffer object when no filesystem bmap exists.
  - `vop_stdvptocnp()` reconstructs a directory name by opening `".."`, reading parent directory entries, matching file IDs, and handling union mount coverage.
  - `dirent_exists()` scans a directory to check whether a named entry exists.
- Buffer, pager, and sync helpers:
  - `vop_stdfsync()` and `vop_stdfdatasync_buf()` flush dirty buffers.
  - `vop_stdgetpages()`, `vop_stdgetpages_async()`, and `vop_stdputpages()` delegate to generic vnode pager routines.
  - `vop_stdread_pgcache()` returns `EJUSTRETURN`.
  - `vfs_stdsync()` iterates mount vnodes and fsyncs dirty ones; `vfs_stdnosync()` is a no-op.
- Allocation/deallocation/advice:
  - `vop_stdallocate()` emulates allocation by reading existing data or zero-filling and writing through the requested range, with partial-progress reporting.
  - `vop_stddeallocate()` emulates deallocation by seeking data/hole ranges and writing zeroes through data ranges.
  - `vp_zerofill()` performs zero writes in bounded chunks.
  - `vop_stdadvise()` handles `POSIX_FADV_DONTNEED` by deactivating VM pages and marking clean/dirty buffers as no-reuse; `WILLNEED` is currently a no-op.
- Poll, kqueue, ioctl, and UNIX socket hooks:
  - `vop_nopoll()` and `vop_stdpoll()` provide simple poll behavior.
  - `vop_stdkqfilter()` delegates to `vfs_kqfilter()`.
  - `vop_stdioctl()` implements default `FIOSEEKDATA` / `FIOSEEKHOLE` behavior for regular files.
  - `vop_stdunp_bind()`, `vop_stdunp_connect()`, and `vop_stdunp_detach()` manage vnode-associated UNIX socket PCB pointers.
- Text and writecount handling:
  - `vop_stdset_text()`, `vop_stdunset_text()`, `vop_stdis_text()`, `vop_stdadd_writecount()`, and `vop_stdadd_writecount_nomsync()` manage `v_writecount`, text-busy protection, lazy msync behavior, and optional vnode references for text mappings.
- Inotify and utility defaults:
  - `vop_stdinotify()` and `vop_stdinotify_add_watch()` delegate to vnode inotify helpers.
  - `vop_stdstat()` builds `struct stat` from `VOP_GETATTR()` and helper pre/post hooks.
  - `vop_stdgetwritemount()`, `vop_stdgetlowvnode()`, and `vop_stdvput_pair()` provide common vnode reference/release behavior.
  - `vop_stdcopy_file_range()` delegates to generic copy-file-range.
- VFS-level defaults:
  - `vfs_stdroot()`, `vfs_stdstatfs()`, `vfs_stdquotactl()`, `vfs_stdvget()`, `vfs_stdfhtovp()`, `vfs_stdextattrctl()`, and `vfs_stdsysctl()` return unsupported defaults.
  - `vfs_stdinit()` and `vfs_stduninit()` are no-ops.
  - `vop_sigdefer()` invokes a vector operation with stop signals deferred.

## Dependencies And Integration
This file is central to vnode/VFS dispatch. It depends on VOP descriptors, vnode locks and reference APIs, buffer cache, generic vnode pager, VM page/object helpers, directory iteration, namei/open helpers, lockf, kqueue, inotify, MAC/audit includes, mount iteration, and generic syscall helpers. Filesystems compose these defaults through their VOP vectors instead of reimplementing common behavior.

## Risk Notes
Defaults are intentionally conservative, but some are only approximations. `vop_stdallocate()` and `vop_stddeallocate()` emulate space operations with reads/writes and may be slower or semantically weaker than filesystem-native implementations. `vop_stdvptocnp()` depends on parent directory scanning and can be expensive or race-prone. Writecount/text transitions rely on atomic state discipline. Filesystems must implement either `vop_access` or `vop_accessx`; otherwise the default access pair can recurse indefinitely as noted in the file.
