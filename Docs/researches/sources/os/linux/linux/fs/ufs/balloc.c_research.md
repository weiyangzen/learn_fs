# File Research: sources/os/linux/linux/fs/ufs/balloc.c

Purpose: UFS fragment/block allocation and freeing.

Key behavior:
- `ufs_free_fragments()` frees a run of fragments within one block, updates fragment summary counts, inode bytes, cylinder group totals, superblock totals, and reassembles a full free block when possible.
- `ufs_free_blocks()` frees whole blocks, handling cylinder group boundary overflow.
- `ufs_change_blocknr()` updates mapped buffer_heads in the page cache when data is moved to a newly allocated block.
- `ufs_clear_frags()` zeroes newly allocated fragments.
- `ufs_new_fragments()` is the main allocator for file growth. It handles already allocated fragments, root reserve checks, preferred cylinder group selection, tail extension, allocation/move fallback, page-cache remapping, and metadata pointer update.
- `ufs_add_fragments()` extends an existing fragment tail in place.
- `ufs_alloc_fragments()` searches preferred, quadratic, then linear cylinder groups and allocates either a full block or fragment run.
- `ufs_alloccg_block()` allocates a full block within a cylinder group, honoring goal/rotor.
- `ufs_bitmap_search()` scans cylinder group free bitmaps using fragment pattern tables.
- `ufs_clusteracct()` maintains 4.4BSD contiguous cluster summaries.
- Static fragment tables encode free-run pattern availability for 8 fragments-per-block and other layouts.

Integration:
- Called by `ufs/inode.c` for block mapping, write allocation, truncation, and block freeing.
- Uses cylinder group cache from `cylinder.c`, on-disk endian helpers, `ufs_buffer_head` helpers, and superblock private info.

Risks and invariants:
- Protected by `UFS_SB(sb)->s_lock` for allocation/free accounting.
- `INVBLOCK` signals internal allocation failure distinct from no-space zero return paths.
- Inode byte accounting is checked via `try_add_frags()` to avoid `i_blocks` overflow.
- Allocation logic is fragment-size sensitive and tightly coupled to UFS cylinder group bitmaps.
