# File Research: sources/os/bsd/freebsd-src/sys/fs/tmpfs/tmpfs.h

Core tmpfs internal header defining directory entries, nodes, mount state, file handles, cookies, locking rules, helper prototypes, and conversion helpers.

Key responsibilities:
- Defines tmpfs VM object flags `OBJ_TMPFS` and `OBJ_TMPFS_VREF` for identifying tmpfs-backed pager objects and vnode references from writable mappings.
- Defines `struct tmpfs_dirent`, which can be a normal RB-tree entry, a synthetic duplicate-hash head, or a duplicate entry on linked lists.
- Defines directory cookie values and bit flags for `.`, `..`, EOF, normal hash cookies, duplicate cookies, and duplicate-head markers.
- Defines extended attribute records with namespace, name, value, and size.
- Defines `struct tmpfs_node`, including inode id, type, attach state, status/access bits, size, attributes, generation, vnode association state, node interlock, refcount, extended attributes, and type-specific union.
- Documents lock ownership for node fields across vnode locks, node interlock, mount all-node lock, and VM object lock.
- Defines type-specific node state for device numbers, directory parent/RB tree/duplicate index/readdir cache/whiteout size, symlink target/SMR allocation flag, and regular-file anonymous VM object/page accounting.
- Defines vnode state bits for allocation, waiters, doomed nodes, and reclaim waits.
- Defines `struct tmpfs_mount`, including max size/pages, pages used, root node, node limit, inode allocator, node count, EA memory accounting, refcount, max file size, used-node list, all-node lock, read-only flag, namecache disable flag, mmap mtime policy, and page-cache read mode.
- Defines packed NFS file-handle data and directory cursor state.
- Declares tmpfs support functions for node/vnode/dirent allocation, directory lookup/iteration, whiteouts, resizing, hole punching, attribute changes, timestamps, memory accounting, init/uninit, and extended attribute cleanup.
- Provides inline conversion helpers from VM objects, mounts, and vnodes to tmpfs objects, plus `tmpfs_use_nc()` and lazy getattr timestamp update.

Dependencies:
- FreeBSD kernel queue/RB tree primitives, malloc declarations, vnode/mount/VM object types, namecache symlink storage, SMR vnode data loading, and tmpfs vnode/fifo operation implementations.

Notable risks:
- Directory cookies are only 31-bit compatible for normal entries and use special duplicate-cookie ranges; collision handling must preserve stable readdir restart behavior.
- Regular-file data is represented by a VM object, so page accounting crosses VFS and VM subsystem boundaries.
- Symlink target storage may be namecache/SMR-backed or malloc-backed; destruction must match the allocation path.
- Node/vnode bidirectional association is protected by `tn_interlock` and state bits; races here affect vnode aliasing and reclaim safety.
