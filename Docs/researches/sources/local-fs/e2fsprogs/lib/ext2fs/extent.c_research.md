# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/extent.c

## Purpose
Implements libext2fs extent-tree support: opening extent handles, traversing extents, inserting/replacing/deleting entries, splitting nodes, setting single-block mappings, fixing parent indexes, repairing checksums, decoding raw extents, and counting blocks.

## Core State
- `struct extent_path`: per-level traversal state with block buffer, entry counts, current pointer, remaining entries, visit state, end logical block, and physical block.
- `struct ext2_extent_handle`: filesystem/inode context, current level, max depth, path stack, and inode buffer.
- `struct ext2_extent_path`: disabled saved-path structure inside `#if 0`.

## Key Operations
- `ext2fs_extent_header_verify`: validates magic, entry count, capacity, and expected max entries.
- `ext2fs_extent_open/open2`: opens an inode extent tree, initializes an empty `i_block` area into an extent root if needed, validates root header, and builds path state.
- `ext2fs_extent_get`: main traversal primitive supporting root/current, sibling movement, next/prev leaf, up/down, last leaf, and depth-first next/prev behavior. Reads child blocks, detects cycles, verifies checksums, and returns generic `struct ext2fs_extent`.
- `update_path`: writes the current path level back either to inode or extent block, updating extent block checksum first.
- `ext2fs_extent_goto/goto2`: descends to the node covering a logical block or leaves the handle near the preceding extent.
- `ext2fs_extent_fix_parents`: propagates changed first logical block values up parent index entries.
- `ext2fs_extent_replace`: overwrites current leaf extent or interior index entry, encoding uninitialized lengths and physical high bits.
- `extent_node_split`: splits full nodes, recursively splits parents if needed, can grow a new root, allocates new extent blocks, writes checksums, adjusts inode block count, and restores original traversal position.
- `ext2fs_extent_insert`: inserts before/after current entry, splitting unless forbidden.
- `ext2fs_extent_set_bmap`: maps, unmaps, or remaps a single logical block, with merge handling for adjacent compatible extents and split handling for middle-of-extent changes.
- `ext2fs_extent_delete`: removes the current extent/index, frees empty non-root nodes, updates parent pointers and inode block count.
- `ext2fs_extent_get_info`: returns current tree and extent capacity information.
- `ext2fs_max_extent_depth`: computes max possible depth for block size.
- `ext2fs_fix_extents_checksums`: traverses extent blocks and rewrites bad checksums when metadata checksums are enabled.
- `ext2fs_decode_extent`: decodes raw on-disk leaf extent into generic form.
- `ext2fs_count_blocks`: counts data extents plus intermediate extent-tree blocks.

## Dependencies
Uses:
- `ext3_extents.h` structs/macros.
- `io_channel_read_blk64/write_blk64`.
- `ext2fs_extent_block_csum_verify/set`.
- `ext2fs_alloc_block2`, `ext2fs_block_alloc_stats2`.
- `ext2fs_iblk_add_blocks`, inode read/write.
- Feature and block-size helpers from `ext2fs.h`/`ext2_fs.h`.

## Risks and Notes
- Traversal state is subtle: `left`, `curr`, and `visit_num` drive depth-first behavior and second-visit flags.
- Parent index starts must be repaired after first-entry logical block changes.
- Node splitting can recursively split parents and grow the root; failure recovery depends on restoring the previous handle position.
- `ext2fs_extent_set_bmap` handles many edge cases: holes, first/last/middle blocks, uninitialized extents, adjacent merges, and rollback on failed middle splits.
- Checksum errors are suppressed only when `EXT2_FLAG_IGNORE_CSUM_ERRORS` is set.
