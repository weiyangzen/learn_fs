# File Research: sources/local-fs/e2fsprogs/e2fsck/jfs_user.h

## Purpose
Compatibility layer allowing e2fsck/debugfs user-space code to include and reuse kernel JBD/JBD2 journal recovery code.

## Key Definitions
- User-space `buffer_head`, `inode`, and `kdev_s` substitutes.
- `K_DEV_FS` and `K_DEV_JOURNAL` device selectors.
- No-op kernel primitives such as buffer locking and readahead.
- Simple `kmem_cache`, `kmalloc`, `kfree`, hash helpers, checksum helper, and descriptor checksum setter.
- Includes `<ext2fs/kernel-jbd.h>` for journal definitions.

## Declared Kernel-Compatibility APIs
Declares functions implemented in `journal.c`:
- `jbd2_journal_bmap`
- `getblk`
- `sync_blockdev`
- `ll_rw_block`
- `mark_buffer_dirty`
- `mark_buffer_uptodate`
- `brelse`
- `buffer_uptodate`
- `wait_on_buffer`

Also declares recovery/revoke APIs supplied by local recovery/revoke sources.

## Integration
Included by `journal.c`, `recovery.c`, and `revoke.c`. With `DEBUGFS`, adapts types to `ext2_filsys`; otherwise uses `e2fsck_t`.

## Risks / Notes
This file intentionally mirrors kernel expectations in user space, so ABI/semantic drift between imported journal code and these shims is a key maintenance risk.
