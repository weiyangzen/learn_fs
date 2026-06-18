# File Research: sources/local-fs/e2fsprogs/e2fsck/e2fsck.8.in

## Purpose
Manual page template for the `e2fsck(8)` command.

## Covered Behavior
Documents:
- ext2/ext3/ext4 checking and journal replay behavior.
- Safety warning for mounted filesystems.
- Interactive repair modes and answers.
- Main options: alternate superblock/blocksize, bad block scanning/list replacement, progress FD, directory optimization, force, flush, external journal, bad block preservation, read-only/no/preen/yes modes, timing, verbose, version, undo files.
- Extended options including `ea_ver`, `journal_only`, `fragcheck`, `discard`, extent optimization toggles, inode count fullmap, readahead, `bmap2extent`, `fixes_only`, `check_encoding`, and `unshare_blocks`.
- Exit code bit meanings.
- SIGUSR1/SIGUSR2 progress control.
- Bug-reporting guidance and `E2FSCK_CONFIG`.

## Integration
Generated to `e2fsck.8` by the makefile using substitution macros for version/date and conditional external journal content.

## Risks / Notes
This file is documentation, but it is also the user-facing contract for many options implemented across `unix.c`, `badblocks.c`, `journal.c`, `extents.c`, pass code, and logging/config code.
