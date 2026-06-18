# File Research: sources/local-fs/ocfs2-tools/fswreck/chain.c

This file injects corruption into OCFS2 chain allocator metadata and superblock cluster counts.

Key behavior:
- `mess_up_sys_file()` reads a bitmap/chain inode, verifies `OCFS2_BITMAP_FL` and `OCFS2_CHAIN_FL`, then mutates chain list, chain record, inode bitmap, or pointed group descriptor fields depending on `fsck_type`.
- Supported chain corruptions include invalid `cl_count`, `cl_next_free_rec`, zero chain head block, bad inode `i_clusters` or `i_size`, bad bitmap used count, out-of-range chain head block, bad group generation, bad group signature, bad group next pointer, bad `c_total`, and bad `cl_cpg`.
- `mess_up_sys_chains()` resolves either the global bitmap system inode or a slot-local inode allocator before calling `mess_up_sys_file()`.
- Public wrappers group corruption families for the dispatcher: chain list, record, inode, group, group magic, and CPG.
- `mess_up_superblock_clusters()` copies the superblock inode block, changes `i_clusters` by roughly 2.5 cluster groups, and writes it directly with `io_write_block()`.
- `mess_up_superblock_clusters_excess()` and `_lack()` choose increment or decrement.

Integration notes:
- Uses libocfs2 system inode lookup, group descriptor reads/writes, and block allocation geometry helpers.
- Some corruption paths require at least one chain record and warn instead of changing metadata if none exists.
- Superblock cluster corruption is marked in `main.c` as needing `nometaecc`, because it writes a copied superblock directly.
