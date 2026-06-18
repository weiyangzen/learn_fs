# File Research: sources/os/linux/linux-stable/fs/ext4/extents.c

This is ext4's core on-disk extent-tree implementation. It manages extent-tree validation, lookup, insertion, splitting, merging, deletion, block mapping/allocation, unwritten extent conversion, fallocate range operations, FIEMAP support, extent swapping, bigalloc cluster handling, and fast-commit replay repair/update helpers.

Major responsibilities:
- Extent metadata integrity: extent-block checksums via `ext4_extent_block_csum*()`, header/entry validation through `__ext4_ext_check()`, and buffer verified-bit handling around journal write access.
- Extent path lifecycle: `ext4_find_extent()` walks inode-rooted extent trees into `struct ext4_ext_path`; `ext4_free_ext_path()` and helpers release path buffer heads.
- Tree search and caching: binary searches index and leaf blocks, optionally caches discovered written/unwritten/hole mappings into the extent status tree, and supports full precache through `ext4_ext_precache()`.
- Tree mutation: `ext4_ext_insert_extent()`, `ext4_ext_split()`, `ext4_ext_grow_indepth()`, `ext4_ext_create_new_leaf()`, `ext4_ext_correct_indexes()`, and merge helpers maintain sorted, non-overlapping extent leaves and parent indexes.
- Block mapping/allocation: `ext4_ext_map_blocks()` is the main extent-backed map/create path. It handles existing initialized extents, unwritten extents, holes, bigalloc implied cluster allocation, allocator requests, insertion, cleanup on allocation/insertion failure, and map flag return semantics.
- Unwritten extent handling: split/convert helpers support buffered writes, direct I/O completion, initialized-to-unwritten conversion, zeroout fallback, and atomic write conversion.
- Truncation and punching: `ext4_ext_remove_space()`, `ext4_ext_rm_leaf()`, `ext4_remove_blocks()`, and `ext4_ext_truncate()` remove extent ranges, free blocks, update indexes, and handle bigalloc partial clusters and pending reservation rerereservation.
- Fallocate operations: `ext4_fallocate()` dispatches allocate, punch, collapse, insert, zero-range, and write-zeroes modes. Collapse/insert shift logical extents left/right after cache invalidation and journaling setup.
- FIEMAP and ES-cache reporting: `ext4_fiemap()`, xattr iomap helpers, `ext4_get_es_cache()`, and `ext4_fill_es_cache_info()` expose file and xattr layout.
- Extent swapping and replay: `ext4_swap_extents()` swaps physical mappings between locked inodes; replay helpers update extents, merge/shrink trees, recalculate `i_blocks`, and rebuild block bitmaps after fast-commit replay.

Important design points:
- The on-disk extent tree is a B-tree rooted in `EXT4_I(inode)->i_data`; depth zero means extents live directly in the inode, while deeper trees use index blocks and leaf extent blocks.
- All extent tree modifications are journaled. Metadata blocks are obtained with journal write/create access and dirtied through `ext4_ext_dirty()`.
- `i_data_sem` is the primary extent-tree mutation lock. Higher-level range operations also rely on `i_rwsem`, invalidate locking, page-cache invalidation, and DIO waits before shifting or punching mappings.
- The extent status tree is kept coherent by inserting/removing cached ranges around allocation, conversion, truncation, collapse, insert, swap, and zeroout paths. `EXT4_EX_NOCACHE` is used while extents are in flux.
- Bigalloc adds cluster-level complexity: logical/physical cluster alignment, implied allocation reuse, partial cluster states, pending reservations, and reserved-cluster rerereservation on free.
- Unwritten extents are first-class states, not holes. Reads and some lookups report them as unwritten, while writes split/convert them into initialized extents or use zeroout fallback when metadata insertion fails.
- Fast-commit replay bypasses normal journal handles in some helpers and directly adjusts extent state, then marks inode metadata dirty.

Key invariants:
- Extent headers must have the correct magic, depth, max/entry counts, and checksum when metadata checksums are enabled.
- Leaf extents and index entries must be ordered and non-overlapping.
- Extents cannot have zero length or wrap logical block space.
- Physical block ranges must pass `ext4_inode_block_valid()`.
- Parent index keys must track the first logical block in child subtrees when leaf starts change.
- Full leaves are split before inserting; root growth copies the old inode-root contents to a new metadata block and installs a single root index.
- Extent merges require matching written/unwritten state, logical adjacency, physical adjacency, and length limits.
- Partial cluster freeing is deliberately conservative to avoid freeing clusters still shared by neighboring extents.

External interfaces exported or used outside this file include extent tree initialization/release, extent lookup, path free, map blocks, truncation, fallocate, FIEMAP, extent conversion, extent swapping, cluster mapped checks, fast-commit replay helpers, and KUnit test exports.
