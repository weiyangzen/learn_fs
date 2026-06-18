# File Research: sources/os/linux/linux/fs/jffs2/summary.c

## Role

Implements optional JFFS2 summary support: compact per-eraseblock metadata used to speed mount-time scanning.

## Key Responsibilities

- Initializes and frees `struct jffs2_summary` and its bounded write buffer in `jffs2_sum_init()` and `jffs2_sum_exit()`.
- Collects in-memory summary records for inode, dirent, xattr, xref, and padding nodes through `jffs2_sum_add_*_mem()` and `jffs2_sum_add_kvec()`.
- Supports disabling/resetting summary collection per eraseblock via `JFFS2_SUMMARY_NOSUM_SIZE`.
- Moves scan-collected summary state into the superblock summary for the selected `nextblock`.
- Processes on-flash summary records in `jffs2_sum_process_sum_data()`, creating inode caches, dirent objects, xattr staging objects, and raw refs.
- Validates summary header, node, and payload CRCs in `jffs2_sum_scan_sumnode()`.
- Writes summary nodes in `jffs2_sum_write_sumnode()` and `jffs2_sum_write_data()`, serializing descriptors, adding the trailing summary marker, padding to consume remaining block space, and linking a summary raw ref.

## Important Interactions

- Called from `scan.c` during mount and from `nodemgmt.c` before retiring a block.
- Fed by `writev.c` and `wbuf.c` for newly written nodes.
- Uses `sum_link_node_ref()` to account for gaps because summary records do not explicitly describe dirty space.

## Invariants and Risks

- Summary size is capped at `MAX_SUMMARY_SIZE` for allocation feasibility.
- Summary nodes are an optimization: CRC failures or unsupported compatible summary entries fall back to full scan.
- Unknown node types in write-time summary collection are programmer errors unless compatible-copy handling disables summary.
- Failed summary writes mark written bytes obsolete when possible and disable summary for the block.
