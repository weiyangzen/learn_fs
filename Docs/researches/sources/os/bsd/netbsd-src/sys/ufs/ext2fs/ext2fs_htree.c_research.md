# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_htree.c

This file implements ext3/ext4 HTree indexed directory lookup and insertion support.

Key public functions:
- `ext2fs_htree_has_idx`: checks whether a directory has HTree indexing enabled.
- `ext2fs_htree_lookup`: looks up a name through the HTree and scans candidate leaf directory blocks.
- `ext2fs_htree_create_index`: converts a full single-block directory into an indexed directory.
- `ext2fs_htree_add_entry`: adds a directory entry through an existing HTree, splitting leaf and index blocks as needed.

Key internal helpers:
- Accessors/mutators for HTree entry hash, block, count, and limit.
- `ext2fs_htree_find_leaf`: traverses root and optional second-level index to find the leaf block for a hash.
- `ext2fs_htree_check_next`: handles hash collisions by advancing to adjacent leaves.
- `ext2fs_htree_split_dirblock`: sorts directory entries by hash, moves roughly half to a new block, computes split hash, and inserts the new entry.
- `ext2fs_htree_insert_entry*`: inserts index entries.
- `ext2fs_htree_append_block`: appends a full directory block through `VOP_WRITE`.
- `ext2fs_htree_writebuf` and `ext2fs_htree_release`: write or release traversal buffers.

Important behavior:
- Only up to one indirect HTree level is supported; deeper indexes return errors.
- Root initialization preserves `.` and `..`, sets `EXT2_INDEX`, initializes root info, and creates entries for blocks 1 and 2.
- If a target index node is full, insertion may split the index node or create a second HTree level.
- If the root index is full at two levels, insertion fails with `EIO`.
- Lookup falls back to scanning next leaves when the collision bit or equal hash indicates possible matches beyond the first target block.

Dependencies:
- Directory layout from `ext2fs_dir.h`.
- Hashing from `ext2fs_hash.c`.
- Vnode/buffer APIs, `ext2fs_blkatoff`, `ext2fs_search_dirblock`, `ext2fs_add_entry`.
- Kernel heap sort and temporary malloc.

Notable implementation risks:
- Directory split/append operations update several blocks and index buffers without journaling; crash consistency is classic ext2-style.
- The code assumes valid directory record lengths while walking blocks.
- Multi-level index support is intentionally limited.
