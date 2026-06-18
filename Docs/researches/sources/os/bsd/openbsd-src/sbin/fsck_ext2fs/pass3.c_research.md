# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ext2fs/pass3.c

Implements ext2 fsck phase 3: directory connectivity repair.

Behavior:
- Walks cached directory inodes in reverse order.
- Finds directories not reachable from root, directories without parents, and directory loops.
- Selects an orphan directory to reconnect.
- Calls `linkup` to attach it to `lost+found`.
- Updates cached parent/dotdot state, adjusts `lost+found` link count accounting, marks the orphan as found, and reruns connectivity propagation.

This pass specifically handles disconnected directory subtrees after pathname validation.
