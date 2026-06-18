# File Research: sources/local-fs/e2fsprogs/e2fsck/util.c

## Purpose
Provides miscellaneous e2fsck utilities: fatal exit handling, logging, allocation wrappers, interactive prompting, bitmap I/O wrappers, resource tracking, inode I/O wrappers, backup-superblock discovery, filesystem/module detection, reliable writes, MMP diagnostics, bitmap type selection, and memory-size detection.

## Main Elements
- `fatal_error()`: flushes/stops MMP, reports modification/error state, sets abort flag, longjmps if safe, otherwise exits with fsck status.
- `log_out()` / `log_err()`: mirror stdout/stderr messages to optional log file.
- `e2fsck_allocate_memory()` and `string_copy()`: common allocation helpers.
- `ask_yn()` / `ask()`: interactive yes/no prompting with raw terminal mode, translated shortcuts, “yes to all”, and cancellation handling.
- `e2fsck_read_bitmaps()` / `e2fsck_write_bitmaps()`: controlled bitmap read/write with e2fsck bitmap type selection and checksum-error handling.
- `preenhalt()`: stops automatic preen mode on unexpected inconsistency.
- `RESOURCE_TRACK` helpers: track memory, CPU time, elapsed time, and I/O deltas.
- Inode wrappers: fatal-on-error read/write helpers for normal and full inode sizes.
- `get_backup_sb()`: scans likely backup superblocks across block sizes and backup group sequence.
- `ext2_file_type()`: maps Linux inode mode to ext2 directory entry file type.
- `fs_proc_check()` / `check_for_modules()`: detect kernel filesystem support via `/proc/filesystems` or modules.
- `write_all()`: retries partial/EINTR/EAGAIN writes.
- `dump_mmp_msg()` / `e2fsck_mmp_update()`: report MMP conflicts and update failures.
- `e2fsck_set_bitmap_type()` plus allocation wrappers: profile-driven bitmap backend selection.
- `get_memory_size()`: returns physical memory size via `sysconf`.

## Dependencies And Integration
Used broadly by e2fsck passes and `unix.c`. Depends on libext2fs memory, bitmap, I/O, inode, MMP, profile, and problem conventions. Reads host `/proc` and `/lib/modules` only for feature/module checks.

## Risk Notes
`fatal_error()` determines final fsck status and whether modifications require reboot/non-destructive flags. Prompt handling changes terminal mode and relies on restoration on normal prompt exit. Bitmap reads intentionally ignore checksum errors during retry, which is useful for repair but shifts validation responsibility to later passes.
