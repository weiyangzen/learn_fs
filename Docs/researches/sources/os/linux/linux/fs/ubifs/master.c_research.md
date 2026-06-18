# File Research: sources/os/linux/linux/fs/ubifs/master.c

## Role

Reads, validates, compares, authenticates, and writes the UBIFS master node. The master node records mount-critical filesystem state, including log/index/LPT/orphan/lprops positions and space accounting.

## Key APIs

- `ubifs_compare_master_node()`
- `ubifs_read_master()`
- `ubifs_write_master()`

## Important Behavior

UBIFS keeps two master-node LEBs. `scan_for_master()` scans both, requires matching node counts, offsets, and master contents, and selects the latest valid master node. The comparison ignores the common header and embedded HMAC because sequence numbers, CRCs, and HMACs differ between mirrored writes.

Authenticated mounts validate either the superblock-recorded master hash, when the HMAC field is zero, or the master-node HMAC.

`ubifs_read_master()` allocates `c->mst_node`, scans or recovers the master node, clears the recovery flag in memory, converts little-endian fields into `struct ubifs_info`, copies the root-index hash, detects the no-orphans flag, handles automatic resize growth, validates all loaded values, and initializes old-index debug checking.

`validate_master()` checks sequence/cmt/inode watermarks, log head, root branch, GC LEB, index head, old index size, LPT root/head/ltab/lsave locations, lscan position, and global free/dirty/used/dead/dark space totals.

`ubifs_write_master()` appends the next master node in the first master LEB, wraps by unmapping when needed, writes with HMAC, and mirrors the same node to the second master LEB at the same offset.

## Dependencies

Interacts with scan/recovery code, authenticated hash/HMAC helpers, node write helpers, superblock authentication metadata, LPT geometry fields, and debug old-index validation.

## Research Notes

Master validation is the mount gate for most UBIFS global invariants. Recovery is delegated to `recovery.c` when the mirrored master area is inconsistent but recoverable.
