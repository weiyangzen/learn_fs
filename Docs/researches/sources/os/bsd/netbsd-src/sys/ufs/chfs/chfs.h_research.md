# File Research: sources/os/bsd/netbsd-src/sys/ufs/chfs/chfs.h

Read completely: 757 lines.

Main kernel header for CHFS, NetBSD's flash-oriented filesystem. It defines mount state, eraseblock/node reference structures, vnode-cache structures, fragment/read-inode helpers, allocation constants, inline flash operation wrappers, and prototypes for the CHFS implementation files.

Core model:
- CHFS pads node lengths to 4-byte boundaries and stores node state in the low two bits of node-reference offsets.
- Vnode cache states track unchecked, checking, present, absent, GC, reading, and clearing states.
- Eraseblock states distinguish free, clean, partially dirty, and all-dirty blocks.
- Node error constants identify bad magic, CRC, and name CRC conditions.

In-memory structures:
- `struct chfs_node_ref` points to on-media nodes by logical eraseblock number and offset; refs are allocated in blocks with sentinel values for empty and linked ref blocks.
- `node_next` walks ref blocks, following `REF_LINK_TO_NEXT` and stopping at `REF_EMPTY_NODE`.
- `struct chfs_dirent` is the in-memory directory entry with node ref, version, target vnode number, name hash, type, name length, and flexible name storage.
- Temporary data-node and read-inode structs support reconstruction of inode fragment trees from scanned media.
- `struct chfs_full_dnode` and `struct chfs_node_frag` represent full data nodes and fragments in rb trees.
- `struct chfs_vnode_cache` links vnode, data-node, and dirent refs, stores version/link/parent/state metadata, and holds scan-time dirent lists.
- `struct chfs_eraseblock` tracks logical eraseblock number, queue membership, unchecked/used/dirty/free/wasted sizes, node-ref bounds, and GC cursor.
- `struct chfs_mount` owns the mount pointer, eraseblock handler, version counters, vnode-cache hash, eraseblock array and queues, global size counters, reserved-block thresholds, GC thread state, write buffer state, pools, locks, and filesystem block constants.

Queues and allocation policy:
- Eraseblocks move through free, clean, dirty, very-dirty, erasable-pending-wbuf, and erase-pending queues.
- Allocation modes distinguish normal writes, deletion, and GC.
- Reserved block fields and dirty-space triggers drive ENOSPC/GC behavior.

Declared implementation surface:
- Build/scan/nodeops/malloc/readinode/erase/GC/VFS/vnops/vnode/vnode-cache/wbuf/write/subr functions are declared here.
- Vnode operation vectors `chfs_vnodeop_p`, `chfs_specop_p`, and `chfs_fifoop_p` are exported.
- Inline helpers wrap EBH map/unmap/read/write and log errors.
- `CHFS_PAGES_MAX` reserves 4 MiB worth of pages before allowing CHFS page use.
- `CHFS_ITIMES`, `IMPLIES`, and `IFF` provide small local helper macros.

Risks and notes:
- Several comments flag incomplete or uncertain design points, including old `void *p` placement, bad-block checks, and TODOs around moving declarations.
- Lock-order comments require mountfields before vnode-cache, size, or write-buffer locks.
- Node-reference pointer tagging in low offset bits requires all real offsets to be accessed through `CHFS_GET_OFS`.
