# File Research: sources/os/bsd/netbsd-src/sys/fs/tmpfs/tmpfs_vnops.c

Read completely: 1373 lines.

This implements tmpfs’s main vnode operations. It defines the normal vnode op table and provides lookup, create, mknod, open, access, getattr, setattr, read/write, remove, link, mkdir, rmdir, symlink, readdir, readlink, inactive, reclaim, pathconf, advlock, getpages, putpages, whiteout, and print.

Lookup uses namecache first, handles `.`, `..`, whiteouts, read-only write denial, sticky-directory delete checks, and vcache lookup by node pointer. Create/mknod/mkdir/symlink call `tmpfs_construct_node`. Read/write use UBC over the node’s UVM object; write resizes before copying and rolls size back on error. Remove/rmdir support whiteout replacement. Readdir delegates cookie handling to `tmpfs_dir_getdents` and optionally returns cookie arrays. Page operations delegate to the UVM anonymous object pager and lazily schedule timestamp updates.

Important interactions: rename is implemented in `tmpfs_rename.c`; node/dirent mechanics live in `tmpfs_subr.c`; FIFO and device nodes use separate operation tables.

Security/reliability notes: access and mutation operations enforce read-only mounts, immutable/append flags, sticky directory rules, link limits, and vnode authorization. The page path checks past-EOF requests and reclaimed-vnode state before invoking the pager.
