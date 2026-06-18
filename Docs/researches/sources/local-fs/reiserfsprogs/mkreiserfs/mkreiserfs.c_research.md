# File Research: sources/local-fs/reiserfsprogs/mkreiserfs/mkreiserfs.c

Implements filesystem creation. It parses CLI options, selects format, validates size/block options, creates the filesystem handle, creates journal and bitmap structures, builds the superblock, bitmap, and root block, reports the resulting layout, confirms destructive writes, wipes old signatures, zeroes the journal, closes/syncs, and reports success.

Important routines:
- `make_super_block()` sets clean state, tree height, hash, UUID/label for 3.6, reserved journal blocks, and free-block adjustment for bad blocks.
- `invalidate_other_formats()` zeroes the initial 64 KiB to remove old signatures.
- `zero_journal()` writes zero-filled journal blocks with progress.
- `make_bitmap()` marks skipped/super/bitmap/journal/bad/root blocks and computes free blocks.
- `make_root_block()` creates an empty leaf, ensures the root directory exists, and marks root object IDs used.
- `report()` prints superblock, journal, hash, free-space, UUID/label, and debug details.

The main path uses `can_we_format_it()`, `block_size_ok()`, `reiserfs_create()`, `reiserfs_create_journal()`, `reiserfs_create_ondisk_bitmap()`, `create_badblock_bitmap()`, and `add_badblock_list()`.
