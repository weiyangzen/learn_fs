# File Research: sources/os/linux/linux-stable/fs/jffs2/summary.c

This file implements optional JFFS2 summary support: compact per-eraseblock metadata used to speed mount-time scanning.

Key responsibilities:
- Initializes and frees `struct jffs2_summary` and its bounded write buffer in `jffs2_sum_init()` and `jffs2_sum_exit()`.
- Collects in-memory summary items for inode, dirent, xattr, xref, and padding nodes through `jffs2_sum_add_*_mem()` and `jffs2_sum_add_kvec()`.
- Supports disabling and resetting summary collection per eraseblock, using `JFFS2_SUMMARY_NOSUM_SIZE` as the disabled sentinel.
- Moves scan-collected summary state into the superblock summary for the selected `nextblock`.
- Processes on-flash summary records in `jffs2_sum_process_sum_data()`, creating inode caches, dirent objects, xattr staging objects, and raw refs without reading every full node.
- Validates summary-node header, node, and payload CRCs in `jffs2_sum_scan_sumnode()` before trusting summary contents.
- Writes summary nodes in `jffs2_sum_write_sumnode()` and `jffs2_sum_write_data()`, serializing collected descriptors, adding a trailing summary marker, padding to consume remaining block space, and linking the summary raw ref.

Important interactions:
- Called from `scan.c` during mount and from `nodemgmt.c` before retiring a `nextblock`.
- `writev.c` and `wbuf.c` feed just-written node kvecs into the summary collector.
- Summary scanning uses `sum_link_node_ref()` to account for gaps because summary data does not explicitly encode dirty space.

Notable invariants and risks:
- Summary size is capped at 64 KiB for kmalloc feasibility.
- Summary nodes are non-fatal optimization data: CRC failures or unsupported compatible summary entries fall back to full block scan.
- Unknown node types in write-time summary collection are treated as programmer errors unless they are compatible-copy nodes, which disable summary for the block.
- Failed summary writes mark written bytes obsolete when possible and disable summary for that block.
