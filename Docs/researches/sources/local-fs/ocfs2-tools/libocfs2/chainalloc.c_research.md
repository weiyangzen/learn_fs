# File Research: sources/local-fs/ocfs2-tools/libocfs2/chainalloc.c

Adapts generic bitmaps to OCFS2 on-disk chain allocators.

Private bitmap data stores the cached allocator inode, dirty state, last error, and whether the bitmap is a suballocator. Region-private data links a bitmap region to its group descriptor, dirty flag, and bit offset within discontiguous groups. Destroy notification frees group descriptors once per discontiguous group head and releases private data.

Read path walks chain groups with `ocfs2_chain_iterate()`, reads each group descriptor, and creates bitmap regions. Contiguous groups become one region; discontiguous groups create one region per extent record, with bit-offset handling and set-bit counts copied from the group bitmap.

Write path copies dirty region bits back into group descriptor bitmaps, preserving unrelated leading/trailing bits for unaligned discontiguous regions, writes dirty group descriptors, then writes the cached allocator inode. Bit-change notification keeps group free count, chain record free count, and inode used count synchronized.

Public APIs load/write chain allocators, allocate/free ranges, allocate/free/test a single bit, force a value, initialize a new group descriptor, and add a new group to a chain. `ocfs2_chain_add_group()` allocates one cluster group, picks a chain, links the new group at the chain head, updates inode accounting, persists it, and rolls back in-memory/disk allocations on failure where possible.
