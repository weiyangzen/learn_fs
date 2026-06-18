# File Research: sources/local-fs/e2fsprogs/e2fsck/journal.c

## Purpose
Handles ext3/ext4 journal discovery, validation, recovery, reset, release, external journal hints, hidden journal inode migration, and ext4 fast-commit replay.

## Kernel Compatibility Layer
Implements `jfs_user.h` shims:
- `jbd2_journal_bmap()` maps journal logical blocks via inode bmap for internal journals.
- `getblk()` allocates user-space buffer heads over filesystem or journal I/O.
- `ll_rw_block()` reads/writes blocks through libext2fs I/O.
- `brelse()` writes dirty buffers before freeing.
- buffer state helpers mirror kernel interfaces.

## Journal Checksums
Provides journal superblock checksum verification and setting for checksum v2/v3 journals, using CRC32C and validating checksum type.

## Fast-Commit Replay
The file implements ext4 fast-commit scan and replay:
- Scan validates tag ordering, expected transaction ID, supported features, extent encodings, and tail CRC.
- Replay handles create/link/unlink dentry tags, inode tags, add-range/delete-range extent tags, padding/head/tail.
- Extent replay keeps a cached `extent_list` per inode, modifies ranges in memory, marks block bitmap allocation state, and flushes via `e2fsck_rewrite_extent_tree()`.
- Replay marks the filesystem temporarily erroneous and `EXT4_FC_REPLAY` because replay updates are not atomic; at completion it recalculates summary stats, writes bitmaps, restores superblock state, updates checksums, and flushes.

## Journal Loading
`e2fsck_get_journal()`:
- Allocates journal and kdev state.
- Handles internal journal inode lookup and fallback to superblock backup journal blocks.
- Handles external journal discovery by UUID/devno and validates external journal superblock, UUID, and metadata checksum.
- Opens journal I/O, reads the journal superblock block, and installs fast-commit callback if enabled.

`e2fsck_journal_load()`:
- Reads journal superblock.
- Verifies magic/type/version/features/checksum.
- Handles v1/v2 compatibility cleanup.
- Sets journal tail, transaction sequence, first/last blocks, and fast-commit region bounds.

## Recovery / Repair
- `e2fsck_check_ext3_journal()` ensures superblock journal fields are consistent, handles missing/bad journal inode, corrupt journal superblock, unsupported features, stale recovery state, nonzero journal start, and journal errno propagation.
- `recover_ext3_journal()` initializes revoke caches/table, loads the journal, runs `jbd2_journal_recover()`, records failed transactions, then releases/reset journal state.
- `e2fsck_run_ext3_journal()` refuses read-only recovery, flushes pending fs modifications, runs recovery, reopens the filesystem because recovery changed disk state, preserves write/error accounting, clears recovery flag, and rechecks journal consistency.

## Journal Inode / External Hint Maintenance
- `e2fsck_move_ext3_journal()` can move visible root-directory journal files such as `.journal` to reserved inode `EXT2_JOURNAL_INO`, after safety checks and user confirmation.
- `e2fsck_fix_ext3_journal_hint()` updates `s_journal_dev` if blkid finds the external journal UUID at a different device number.

## Integration
Central to ext3/ext4 recovery before full checking. Uses `problem.c` prompts, libext2fs I/O/bitmap/inode APIs, imported JBD2 recovery/revoke code, and extent helpers from `extents.c`.

## Risks / Notes
- Fast-commit replay intentionally bypasses normal full-check atomicity and temporarily marks filesystem error state during replay.
- External journal correctness depends on blkid lookup and UUID/device validation.
- The dentry replay path for symlinks deserves attention: the symlink branch returns `EXT2_FT_SYMLINK` directly rather than assigning `filetype`, which reads like a possible logic issue.
