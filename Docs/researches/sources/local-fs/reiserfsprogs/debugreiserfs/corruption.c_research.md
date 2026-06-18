# File Research: sources/local-fs/reiserfsprogs/debugreiserfs/corruption.c

Implements interactive and scripted ReiserFS corruption injection for testing `reiserfsck`.

Main entry points:
- `do_corrupt_one_block(fs, fline)`: corrupts a selected leaf block or edits the superblock if the target block is the superblock.
- `do_one_corruption_in_one_block(...)`: parses single-letter corruption commands.
- `do_leaves_corruption`, `do_bitmap_corruption`, `do_fs_random_corrupt`: random corruption drivers.

Supported targeted corruptions include:
- Editing superblock and journal parameters.
- Changing hash code.
- Cutting directory entries.
- Clobbering directory-entry hashes.
- Changing item type/format/objectid.
- Breaking indirect item pointers.
- Deleting items.
- Making item key order invalid.
- Corrupting old-format stat-data size/first-direct-byte fields.
- Zeroing bytes in item headers or block headers.

Random corruption modes cover:
- Bitmap blocks.
- Leaf block headers.
- Item headers.
- Directory item bodies.
- Stat-data item bodies.
- Indirect item bodies.

Dependencies:
- Uses `debugreiserfs.h` shared mode/data accessors.
- Relies on `reiserfscore` buffer, bitmap, item, key, and directory helpers.
- Uses global `fs` through macros in some helper paths.

Notable risks/quirks:
- It is intentionally destructive and opens the filesystem read-write.
- `corrupt_block_header` ignores the requested offset when calling `memset`; it zeroes from the block header start.
- Many command parsers use loose bounds checks such as `item_num > nr_items`, allowing `item_num == nr_items`.
- Random functions repeatedly seed with `time(NULL)`, reducing randomness if invoked close together.
