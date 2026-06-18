# File Research: sources/os/bsd/netbsd-src/lib/libp2k/p2k.c

Implements "puffs to kernel": a bridge that exposes rump-kernel file systems through PUFFS. It translates PUFFS filesystem/node operations into rump VFS/VOP calls while maintaining vnode identity and references.

Mount state tracks the PUFFS usermount, optional `ukfs`, rump mount, root vnode, debug flags, tmpfs special handling, and a 65536-bucket hash from vnode pointer to `p2k_node`. `getp2n` preserves one puffs node per vnode and releases lookup references when an existing node is found.

Initialization registers PUFFS ops, reads `P2K_*` environment controls, optionally daemonizes, initializes rump, and sets caller/lwp hooks. Setup mounts either a real ukfs-backed filesystem or the rump root for `rumpfs`, creates the root node, configures file-handle passthrough, and enters the PUFFS mount/mainloop path.

Most node operations are direct wrappers: lookup, create/mknod/mkdir/symlink, open/close/access/getattr/setattr/fsync/mmap/seek, remove/link/rename/rmdir, readdir/readlink/read/write, pathconf, and extattr operations. They build rump credentials and componentnames from PUFFS inputs, use appropriate vnode locks, and convert uio/resid values.

The inactive/reclaim path is critical: inactive flushes cached pages except for tmpfs, calls rump inactive, and if the filesystem asks for recycle it releases the vnode and tells PUFFS no reference remains. Reclaim releases any remaining vnode, removes the node from the hash, and frees it.
