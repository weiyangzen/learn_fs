# File Research: sources/os/linux/linux-stable/fs/jffs2/scan.c

This file performs mount-time flash scanning, discovers JFFS2 nodes, builds initial inode caches/raw refs, and classifies eraseblocks for allocation and GC.

Key responsibilities:
- `jffs2_scan_medium()` obtains either an XIP-style mapped flash pointer or an allocated scan buffer, scans every eraseblock, resets per-block summary collection, and files blocks into free, clean, dirty, very-dirty, erasable, erase-pending, or bad lists.
- Preserves the best partially dirty block as `c->nextblock`, moving previous candidates to dirty lists and preserving collected summary metadata for the chosen nextblock.
- Refuses to erase a filesystem that appears to contain no valid JFFS2 nodes unless the block mix proves it is simply empty.
- `jffs2_scan_eraseblock()` checks NAND OOB cleanmarkers and bad-block status, attempts summary-node scan first, and falls back to a full node-by-node scan when no valid summary exists.
- Full scan recognizes erased regions, cleanmarkers, padding, inode nodes, dirent nodes, xattr/xref nodes, obsolete nodes, endian/old/dirty magic patterns, unknown compatible/incompatible feature nodes, and bad CRCs.
- `jffs2_scan_inode_node()` validates inode-node CRCs, creates/fetches inode caches, links unchecked raw refs, updates pseudo-random rotation seed, and records summary info.
- `jffs2_scan_dirent_node()` validates dirent and name CRCs, creates parent inode caches, links raw refs with dirent state, and stores scan dirents.
- Xattr scanning creates datum/ref staging objects when xattr support is enabled.
- `jffs2_rotate_lists()` rotates allocator/GC lists based on a pseudo-random seed derived from node versions to spread wear.

Important interactions:
- Calls summary reader/writer collection helpers, raw-node-ref allocation/linking, dirty-space accounting, NAND cleanmarker helpers, xattr setup, and GC trigger logic.
- The block classification returned by `jffs2_scan_classify_jeb()` drives later allocator behavior in `nodemgmt.c`.

Notable invariants and risks:
- Scanner helper functions must advance offsets and update dirty/used/unchecked/free accounting consistently.
- Header CRC is trusted enough to determine `totlen`; node/data/name CRC failures then mark the node space dirty rather than aborting mount.
- Unknown read-only-compatible nodes force a read-only mount; incompatible nodes abort.
- Summary fallback must reset accounting and raw refs if summary content contains unsupported compatible node types.
