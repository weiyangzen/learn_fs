# File Research: sources/os/linux/linux-stable/fs/ubifs/master.c

## Summary
Reads, validates, compares, authenticates, recovers, and writes the replicated UBIFS master node.

## Key APIs
- `ubifs_compare_master_node()`.
- `ubifs_read_master()`.
- `ubifs_write_master()`.

## Important Behavior
UBIFS stores two master-node copies in adjacent master LEBs. `scan_for_master()` scans both, selects the latest valid master node only when node counts, offsets, and payload fields agree, and returns `-EUCLEAN` when recovery is needed. `ubifs_compare_master_node()` intentionally skips the common node header and embedded HMAC because sequence numbers, CRCs, and HMACs differ between the two copies.

Authenticated mounts verify either the superblock-stored master hash when the HMAC field is zero or the master node HMAC otherwise.

`ubifs_read_master()` allocates `c->mst_node`, scans or recovers it, clears the recovery flag, transfers all little-endian master fields into `ubifs_info`, copies the root index hash, handles the `UBIFS_MST_NO_ORPHS` flag, and adjusts free-space counters when the volume has grown since the last write.

`validate_master()` checks sequence-number watermarks, inode-number watermarks, log/index/LPT/lsave/head locations, index size, GC and lscan LEBs, and aggregate space accounting.

`ubifs_write_master()` appends the next master node to both master LEBs, unmapping when the next aligned master node would overflow, updates `highest_inum` and root index hash, and writes both copies with HMAC support.

## Dependencies
Calls scan/recovery code, authenticated hash/HMAC helpers, endian conversion helpers, node dump/debug functions, and old-index debug initialization.

## Risks
Mount correctness depends on strict agreement between the two master copies. Validation protects later LPT, replay, orphan, and index code from out-of-range persistent pointers. Write ordering uses duplicated writes for recoverability but still depends on `recovery.c` handling interrupted updates.
