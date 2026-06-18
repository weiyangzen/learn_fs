# File Research: sources/local-fs/e2fsprogs/misc/e2undo.8.in

## Purpose
Manual page template for `e2undo`, which replays an undo log onto an ext2/ext3/ext4 filesystem.

## Documented Interface
- `e2undo [-f] [-h] [-n] [-o offset] [-v] [-z undo_file] undo_log device`

## Options
- `-f`: skip safety check that filesystem superblock matches the undo log.
- `-h`: display usage/header information.
- `-n`: dry run.
- `-o offset`: filesystem byte offset in the target.
- `-v`: print block replay information.
- `-z undo_file`: create a new undo file while replaying, so replay itself can be undone.

## Notes
- Warns that undo files do not recover from power or system crashes.
- References `mke2fs` and `tune2fs`.
