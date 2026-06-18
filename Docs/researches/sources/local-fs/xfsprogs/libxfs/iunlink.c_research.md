# File Research: sources/local-fs/xfsprogs/libxfs/iunlink.c

Userspace helpers for logging/updating XFS per-AG unlinked inode list pointers.

Key responsibilities:
- Updates an inode cluster buffer’s `di_next_unlinked` field safely.
- Verifies the old ondisk pointer before replacement.
- Logs the exact inode buffer byte range modified.
- Reloads the next unlinked inode and sets its in-core previous pointer.

Important behavior:
- Stale inode buffers are not relogged to avoid clearing stale state.
- Updating to the same non-NULL next pointer is treated as corruption.
- `xfs_iunlink_reload_next` verifies the reloaded inode has zero links.

Dependencies:
- Uses libxfs inode mapping/loading, transaction buffer logging, AG/perag state, and tracepoints.

Notable risks:
- This maintains a linked list in metadata; stale old pointers indicate corruption.
- Header-side lookup is stubbed out, so this path does not provide a real inode-cache lookup.
