# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_extent.c

Extent tree implementation for ext4 file block mapping. It verifies extent nodes, searches paths, iterates extents, grows and splits extent trees, inserts/removes mappings, converts unwritten extents, merges adjacent extents, allocates contiguous data blocks, and serves logical-to-physical block requests.

Key behavior:
- Computes and validates extent block metadata checksums using filesystem UUID seed, inode number, generation, and extent block contents up to the tail.
- `ext4_extent_find_extent` walks from the inode-embedded root down to a leaf, binary-searching index/leaf nodes and returning a full path for later modification.
- Path helpers mark extent blocks or inode roots dirty, release loaded blocks, reload invalidated child paths, and increment/decrement to adjacent extents.
- `ext4_extent_grow_tree` moves the inode root into a new extent block and creates a deeper root index in the inode.
- `ext4_extent_split` preallocates tree blocks, grows the tree if needed, splits full leaves/internal nodes, adjusts path pointers, and writes new parent indexes.
- `ext4_extent_insert` inserts one extent into the leaf, splitting first if needed, then updates parent first-key indexes.
- `ext4_extent_remove_space` removes mappings over a logical range, trims partially overlapping extents, frees physical blocks, deletes empty nodes, and collapses empty roots.
- `ext4_extent_convert_written` converts all or part of an unwritten extent to written, zeroing physical blocks and splitting into written/unwritten extents as required.
- `ext4_extent_get_blocks` is the main map/create entry point: finds existing extents, returns holes for reads, allocates new contiguous physical blocks for writes, and appends/prepends/creates extent records.

Notable dependencies:
- Block allocation/freeing from `ext4_balloc.c`.
- Block IO/cache through `ext4_blockdev` and `ext4_trans`.
- Inode flags/root headers from `ext4_inode` and `ext4_super`.

Research notes:
- `ext4_extent_alloc_datablocks` tracks `retnblocks` but returns `nblocks` through `*nblocksp`; if contiguous allocation stops early without an error, callers can believe more blocks were allocated than actually were.
- `ext4_extent_split` leaks the temporary `newfblocks` array if allocation of one of the new blocks fails before reaching the common cleanup label.
- `ext4_extent_find_extent` verifies loaded child blocks, but on verification failure it releases only blocks already represented in the path; the just-loaded failing block is not yet in the path, so that cache reference is at risk.
- The code uses several assertions for extent tree invariants and two insertion cases after pre-splitting; corrupted filesystems can therefore hit assertions depending on build configuration.
