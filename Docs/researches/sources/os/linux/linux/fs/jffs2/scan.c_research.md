# File Research: sources/os/linux/linux/fs/jffs2/scan.c

## Role

Performs mount-time flash scanning, discovers JFFS2 nodes, builds initial inode caches/raw refs, and classifies eraseblocks for allocation and GC.

## Key Responsibilities

- `jffs2_scan_medium()` maps or buffers flash, scans every eraseblock, resets per-block summary collection, and files blocks into free, clean, dirty, very-dirty, erasable, erase-pending, or bad lists.
- Preserves the best partially dirty block as `c->nextblock` and moves previous candidates to dirty lists.
- Refuses to erase a filesystem with no valid JFFS2 nodes unless the block mix proves it is simply empty.
- `jffs2_scan_eraseblock()` checks NAND OOB cleanmarkers/bad-block state, attempts summary scan first, then falls back to full node-by-node scan.
- Full scan recognizes erased regions, cleanmarkers, padding, inode nodes, dirent nodes, xattr/xref nodes, obsolete nodes, endian/old/dirty magic, unknown compatible/incompatible nodes, and bad CRCs.
- `jffs2_scan_inode_node()` validates inode node CRC, creates/fetches inode cache, links unchecked raw refs, and records summary information.
- `jffs2_scan_dirent_node()` validates dirent and name CRCs, creates parent inode cache, links raw refs with dirent state, and stores scan dirents.
- Xattr scanning stages xattr datum/ref objects when enabled.
- `jffs2_rotate_lists()` pseudo-randomly rotates allocator/GC lists to spread wear.

## Important Interactions

- Calls summary scan/write collection helpers, raw-node-ref allocation/linking, dirty-space accounting, NAND cleanmarker helpers, xattr setup, and GC trigger logic.
- `jffs2_scan_classify_jeb()` returns block states consumed by `jffs2_scan_medium()` and allocator behavior in `nodemgmt.c`.

## Invariants and Risks

- Scanner helpers must advance offsets and update dirty/used/unchecked/free accounting consistently.
- Header CRC is trusted enough to determine `totlen`; later node/data/name CRC failures make space dirty rather than aborting mount.
- Read-only-compatible unknown nodes force read-only mounting; incompatible nodes abort.
- Summary fallback resets accounting and raw refs if summary content cannot be used safely.
