# File Research: sources/windows/reactos/sdk/lib/fslib/ext2lib/Mke2fs.c

This file is the top-level ext2 formatter implementation.

Core responsibilities:
- Defines formatter defaults, block/inode ratio policy, and helper logarithm functions.
- `set_fs_defaults` selects block size and inode ratio based on filesystem size/type.
- `zero_blocks` writes zero-filled filesystem blocks through a cached static buffer.
- `zap_sector` clears boot/metadata sectors while preserving a BSD disklabel at sector 0 if detected.
- `ext2_mkdir`, `create_root_dir`, and `create_lost_and_found` create initial directories.
- `write_primary_superblock`, `ext2_update_dynamic_rev`, and `ext2_flush` write primary/backup superblocks, group descriptors, and bitmaps.
- `Ext2DataBlocks` and `Ext2TotalBlocks` convert between total allocated blocks and data blocks accounting for indirect metadata blocks.
- `Ext2Format` opens the volume, reads geometry, initializes ext2 metadata, locks/dismounts the volume, builds root structures, writes metadata, and cleans up.
- `Ext2Chkdsk` is an unimplemented stub returning success.

Important control flow:
- `Ext2Format` computes block count from partition length and selected ext2 block size, computes inode count from `inode_ratio`, reserves 5% blocks, initializes the superblock, zaps boot sectors, assigns UUID/label, allocates metadata tables, zeros old metadata near the end, creates root and `lost+found`, reserves inodes, creates bad-block inode, flushes metadata, then unlocks/dismounts/close.
- Slow format is explicitly not supported; `QuickFormat` mainly controls logging.

Risk points:
- `uuid_generate` currently returns all zeroes, so the jitter and filesystem UUID are not unique.
- `create_journal_dev` is effectively dead code because `retval` starts false and immediately returns.
- The global `bLocked` is not reset per call and can affect cleanup if multiple operations occur in one process.
- `Ext2Chkdsk` reports success despite being unimplemented.
- Label conversion ignores conversion failure/truncation beyond the fixed 16-byte ext2 label field.
