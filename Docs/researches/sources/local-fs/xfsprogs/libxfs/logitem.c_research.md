# File Research: sources/local-fs/xfsprogs/libxfs/logitem.c

Minimal userspace buffer and inode log item support for libxfs transactions.

Key responsibilities:
- Defines buffer and inode log item slab caches.
- Finds matching buffer log items already attached to a transaction.
- Initializes buffer log items and marks buffer byte ranges dirty.
- Initializes inode log items.
- Implements inode log item precommit handling that applies timestamp/version/bigtime/hint fixes and pins the inode cluster buffer.
- Provides inode log item sorting by inode number for deterministic precommit lock ordering.

Important behavior:
- Buffer log item ops are mostly empty because userspace does not write a real journal.
- `xfs_buf_item_log` marks the buffer item dirty but does not maintain a detailed bitmap here.
- Inode precommit upgrades bigtime-capable inodes, clears invalid realtime extent-size/cowextsize hint combinations, attaches inode cluster buffers late, and rolls dirty flags into `ili_fields`.
- Late inode-buffer attachment preserves AGI/AGF/inode-cluster lock ordering.

Dependencies:
- Uses transaction item lists, libxfs buffers, inode mapping, inode fork/buffer code, spin locks, and log item infrastructure.

Notable risks:
- Correct precommit ordering is critical to avoid lock-order inversions with unlinked inode and directory transactions.
- This is a compatibility subset of kernel log item behavior; callers must not assume full journal semantics.
