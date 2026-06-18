# File Research: sources/os/bsd/freebsd-src/sys/fs/unionfs/union_subr.c

Unionfs support routines for vnode caching, node lifecycle, copy-up, whiteouts, and directory checks.

Key responsibilities:
- Initializes and tears down deferred vnode release infrastructure and reports `vfs.unionfs_ndeferred`.
- Maintains small per-directory hash caches for unionfs directory vnodes keyed by upper/lower vnode.
- Implements `unionfs_nodeget` and `unionfs_noderem`, including vnode construction, lock sharing, root marking, cache insertion/removal, writecount cleanup, child cache cleanup, and deferred parent release.
- Tracks per-process node status for lower/upper open counts and readdir state.
- Computes upper vnode attributes according to mount copy mode.
- Provides relookup helpers, in-progress flag coordination, and safe forwarded-VOP reference/lock recovery helpers.
- Implements shadow directory creation, whiteout creation, regular-file copy-up, symlink copy-up, file content copy, and lower-directory emptiness checks against upper whiteouts.

Dependencies:
- Depends on FreeBSD vnode locking, namei/relookup, taskqueue, mount write suspension, MAC hooks, dirent helpers, credentials, and VFS/VOP APIs.
- Depends on `union.h` structures and the unionfs vnode operations vector.

Notable risks:
- This file is highly lock-order sensitive because unionfs vnodes share underlying vnode locks and may span two filesystems.
- Forced unmount and vnode doom paths require special forwarded-VOP handling to avoid returning with unionfs vnodes unlocked or losing base vnode references.
- Copy-up and shadow directory creation temporarily drop locks and use in-progress flags; missed wakeups or incorrect flag cleanup can block or duplicate operations.
- Several comments document imperfect or unresolved locking tradeoffs, especially around cross-filesystem parent/child locking and rmdir lower/upper checks.
- Deferred release means node memory and parent vnode references may outlive reclaim until the taskqueue drains.
