# File Research: sources/os/bsd/dragonflybsd/sys/vfs/tmpfs/tmpfs_subr.c

This file implements TMPFS support routines for node allocation/free, directory entries, vnode allocation, file creation, directory indexing, resizing, attribute changes, timestamps, truncation, inode assignment, RB-tree comparison, and rename lock ordering.

`tmpfs_alloc_node` enforces node limits, allocates a per-mount tmpfs node, initializes common attributes and timestamps, assigns an inode, and initializes type-specific storage. Regular files receive a swap-pager VM object with `OBJ_NOPAGEIN`; symlinks copy their target; directories initialize name and cookie RB trees.

`tmpfs_free_node` removes the node from the used list, releases type-specific resources, deallocates VM objects or symlink targets, clears root references, updates page accounting, destroys locks, and frees the node object. Directory entries are separately allocated/freed by `tmpfs_alloc_dirent` and `tmpfs_free_dirent`, which update target link counts.

`tmpfs_alloc_vp` ensures one active vnode per node. It handles races against existing vnodes, avoids deadlocks when called while holding a directory node lock, initializes vnode type and VMIO/KVABIO state for regular files, assigns FIFO ops for FIFOs, and links node/vnode bidirectionally.

`tmpfs_alloc_file` combines node allocation, dirent allocation, vnode allocation, and directory attachment for create/mkdir/mknod/symlink paths. Directory attachment/detachment maintains both RB trees, parent pointers, link counts, directory sizes, and timestamp status flags.

Directory helpers synthesize `.`/`..`, look up entries by name or cookie, and emit dirents with DragonFly `vop_write_dirent`. `tmpfs_reg_resize` manages file growth/truncation, per-mount page accounting, vnode buffer extension/truncation, backing aobj size, swap free-space cleanup, and small-file block-size growth up to `TMPFS_BLKSIZE`.

Attribute helpers implement chflags, chmod, chown, chsize, chtimes, timestamp flushing, and truncate semantics. `tmpfs_lock4`/`tmpfs_unlock4` impose a deterministic lock order for rename across source directory, target directory, source node, and optional target node.
