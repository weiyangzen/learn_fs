# File Research: sources/os/bsd/dragonflybsd/sys/vfs/fuse/fuse_node.c

Implements FUSE node allocation, RB-tree indexing by inode number, vnode creation/reuse, truncation, and objcache lifecycle.

The RB tree is generated with `RB_PROTOTYPE2` and `RB_GENERATE2`, comparing `struct fuse_node` by `ino`.

`fuse_node_new` allocates and zeroes a node, initializes the node lock, stores mount/inode/type/default state, inserts it into the mount’s node tree, and returns it. `fuse_node_free` removes a node from the tree under `ino_lock` and returns it to the objcache.

`fuse_alloc_node` finds or creates a node for a looked-up inode, rejects block/character/FIFO types, asserts the parent is a directory, and returns a locked vnode via `fuse_node_vn`. If vnode creation fails for a newly allocated node, it frees the node.

`fuse_node_vn` returns an exclusively locked vnode for a node. It handles races where another thread attaches a vnode, uses `vhold/vget/vdrop` for existing vnodes, allocates new vnodes with `getnewvnode`, sets `v_type` and `v_data`, initializes VMIO for regular files, and marks unsupported special/FIFO cases with assertions.

`fuse_node_truncate` updates cached size/attr size and calls `nvtruncbuf` or `nvextendbuf` to update vnode buffers for shrink/grow operations.

`fuse_node_init` and `fuse_node_cleanup` create/destroy the node objcache.

Important dependencies: FUSE mount node tree and locks from `fuse.h`, vnode allocation and VM buffer APIs, and vnode reclaim behavior from `fuse_vnops.c` outside this group.

Notable risks or research hooks: `fuse_node_new` inserts into the RB tree without taking `ino_lock`; callers must already serialize as needed. Special vnode types currently assert, so CUSE/special-file support is incomplete.
