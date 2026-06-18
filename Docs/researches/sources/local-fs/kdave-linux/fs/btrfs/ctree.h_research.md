# File Research: sources/local-fs/kdave-linux/fs/btrfs/ctree.h

Primary in-memory Btrfs tree header defining path state, root state, root structure fields, tree sizing helpers, and the public ctree manipulation API.

Key responsibilities:
- Defines readahead modes for B-tree searches, including backward, forward, and full forward traversal modes.
- Defines `struct btrfs_path`, including nodes, slots, lock state, lowest level, readahead behavior, commit-root search flags, lock-retention flags, split/extension flags, and nowait mode.
- Provides cleanup macros for automatic path freeing or release.
- Enumerates `btrfs_root` state bits for transaction setup, shareability, dirty tracking, deletion, defrag, force-COW, log-tree state, qgroup flushing, orphan cleanup, unfinished drops, and relocation lockdep reset.
- Defines `struct btrfs_qgroup_swapped_blocks` and the large `struct btrfs_root`, covering tree roots, log roots, inode/delayed-node indexes, dirty lists, logging state, defrag progress, delalloc/ordered extents, relocation, send/dedupe/snapshot controls, qgroup reservations, swapfiles, and debug fields.
- Provides root flag and generation helpers using endian-aware fields and READ/WRITE_ONCE for concurrently read log transaction fields.
- Defines extent replacement and drop-extents argument structures used by file extent update paths.
- Defines leaf/node sizing helpers and maximum item/xattr calculations from filesystem node size.
- Declares core ctree APIs for search, COW, copy root, insert/delete, item mutation, traversal, path lifecycle, and old tree walks.
- Provides batch insertion structure and inline wrappers for single-item insertion/deletion and next-leaf/item traversal.
- Provides helpers identifying filesystem roots and data relocation roots.

Dependencies:
- Includes Linux cleanup, spinlock, rbtree, mutex, wait, list, atomic, xarray, and refcount APIs.
- Includes UAPI `linux/btrfs_tree.h`, plus Btrfs locking and accessors.
- Forward-declares major Btrfs structures to expose the ctree API without pulling full subsystem headers.

Notable risks:
- `struct btrfs_root` is a central cross-subsystem structure; field semantics and locking comments are part of many implicit contracts.
- Path flags strongly affect locking, COW, restart, and commit-root behavior; invalid flag combinations can deadlock or expose stale tree blocks.
- Several inline helpers depend on little-endian disk-key layout optimizations and must stay synchronized with on-disk structures.
