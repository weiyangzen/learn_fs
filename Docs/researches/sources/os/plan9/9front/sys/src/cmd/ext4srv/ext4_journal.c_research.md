# File Research: sources/os/plan9/9front/sys/src/cmd/ext4srv/ext4_journal.c

JBD/JBD2-style journal implementation for ext4srv. It loads the journal inode, verifies and writes journal metadata checksums, replays committed transactions, manages revoke records, starts/stops journaling sessions, records dirty buffers into transactions, writes descriptor/data/revoke/commit blocks, and checkpoints completed transactions back to the main filesystem.

Key behavior:
- Defines replay-only revoke entries and runtime recovery state using red-black trees.
- Implements journal superblock, descriptor/revoke metadata, commit block, and data block checksum handling for checksum v1/v2/v3 style feature combinations.
- `jbd_get_fs` binds the journal inode and reads/verifies the journal superblock.
- `jbd_recover` scans valid transactions, builds the revoke tree, replays descriptor data blocks while respecting revokes, clears ext4 `RECOVER`, and advances the journal start.
- Journal block IO maps journal logical blocks through the journal inode with `jbd_inode_bmap` and uses temporary/flushed cache buffers.
- Tag parsing/writing supports 32-bit and 64-bit block numbers, optional UUID fields, escape flags, and last-tag markers.
- `jbd_journal_start` marks the filesystem as needing recovery, initializes transaction IDs and checkpoint queues, and attaches the journal to the block device.
- `jbd_journal_stop` flushes checkpoint transactions, clears recovery state, zeros live journal state, and writes the JBD superblock.
- Transaction code tracks dirty buffers by filesystem LBA, handles ownership when later transactions supersede earlier ones, writes descriptors and data copies to the journal, writes revoke blocks, emits commit blocks, and uses cache write completion callbacks for checkpoint advancement.

Notable dependencies:
- Block cache callbacks and dirty flags from `ext4_bcache`.
- Main filesystem mapping and block IO from `ext4_fs` and `ext4_blockdev`.
- On-disk JBD structures and feature bits from `include/ext4_types.h`.
- Runtime queues and red-black trees from `queue.h` and `tree.h`.

Research notes:
- The code comments still include a stale note elsewhere that lwext4 journaling is not supported, but this file implements a working local JBD layer.
- Journal-device support is explicitly TODO; the journal is expected to be the filesystem journal inode.
- Several writeback/recovery error paths use `assert` for conditions that would be I/O or allocation failures in production.
- `jbd_replay_block_tags` has special handling for block 0 as the ext4 superblock image and preserves mount count/state across replay.
