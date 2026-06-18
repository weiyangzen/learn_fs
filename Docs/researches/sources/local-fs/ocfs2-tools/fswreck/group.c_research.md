# File Research: sources/local-fs/ocfs2-tools/fswreck/group.c

This file injects allocation group descriptor and global bitmap corruptions.

Key behavior:
- `create_test_group_desc()` allocates one cluster and writes a cloned group descriptor at that block, with adjusted `bg_blkno` and cleared `bg_next_group`.
- `damage_group_desc()` reads a bitmap chain inode, finds the first chain record and group descriptor, then mutates group linkage and fields.
- Supported descriptor corruptions include missing expected descriptor, unexpected fake descriptor, bad generation, bad parent dinode, bad block number, bad chain number, self-looped group chain, and impossible free-bit count.
- `mess_up_group_desc()` resolves either the global bitmap or a slot inode allocator, then calls `damage_group_desc()`.
- Public wrappers split minor field, generation, list, cluster group descriptor, and cluster allocation bit corruption.
- `mess_up_cluster_group_desc()` allocates clusters, locates their group descriptor, then inflates `bg_free_bits_count`.
- `mess_up_cluster_alloc_bits()` allocates a cluster without using it later, leaving global bitmap bits marked.

Integration notes:
- Used by `corrupt_group_desc()` and some bitmap-related prompt codes.
- Depends on OCFS2 chain allocator structures and group bitmap sizing.
- Some paths write cloned/fake descriptors directly, so generated test volumes may contain extra allocated-but-inconsistent metadata.
