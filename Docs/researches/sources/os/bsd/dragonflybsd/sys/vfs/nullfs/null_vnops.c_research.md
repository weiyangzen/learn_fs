# File Research: sources/os/bsd/dragonflybsd/sys/vfs/nullfs/null_vnops.c

This file implements nullfs vnode/namecache forwarding operations. The historical comment explains that DragonFly nullfs no longer maintains private null vnodes for most operations; instead, it uses the namecache API and rewrites operation dispatch to the lower mount’s normal vnode ops.

Implemented forwarding wrappers cover namecache operations: resolve, create, mkdir, mknod, link, symlink, whiteout, remove, rmdir, and rename. Rename validates that source and target nullfs mounts forward to the same lower mount before dispatching.

`null_mountctl()` handles export-setting locally through `nullfs_export()` and mount flags via `vop_stdmountctl()`.

Research notes: this is a minimal, namecache-oriented loopback layer, not a general-purpose overlay vnode framework.
