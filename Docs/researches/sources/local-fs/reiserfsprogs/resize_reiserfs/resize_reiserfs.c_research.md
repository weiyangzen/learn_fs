# File Research: sources/local-fs/reiserfsprogs/resize_reiserfs/resize_reiserfs.c

Main program for the ReiserFS resize utility. It parses options, opens the filesystem and journal, chooses online/offline resize mode, validates target size, and dispatches to expansion or shrink logic.

Major responsibilities:
- Parses target size strings in `calc_new_fs_size()`, supporting absolute or relative byte values with K/M/G suffixes.
- Reports old/new superblock state through `sb_report()`.
- Conditionally writes dirty buffers through `bwrite_cond()`.
- Expands filesystems in `expand_fs()` by expanding the bitmap, updating free/block counts, marking new bitmap blocks used, and dirtying the bitmap.
- Validates target size in `resizer_check_fs_size()`.
- Coordinates all resize flow in `main()`.

Important implementation details:
- Opens filesystem read-only first, then opens journal, validates journal parameters unless `-k` skip-journal is set.
- Rejects old non-spread bitmap format.
- If mounted, closes the filesystem and calls the online remount frontend.
- Offline resize requires clean/consistent filesystem state.
- Expansion marks the filesystem `FS_ERROR`, updates bitmap/superblock, then final code restores `FS_CONSISTENT`.
- Shrink delegates to `shrink_fs()`.

Dependencies and interactions:
- Uses `resize.h`, shared ReiserFS core open/journal/bitmap/superblock helpers, and `do_shrink.c`/`fe.c`.
- Depends on device-size helpers like `count_blocks()` and `valid_offset()`.

Risks and notes:
- In the getopt switch, case `'j'` sets `jdevice_name = optarg` and falls through into case `'f'`, so specifying `-j` also sets `opt_force = 1`.
- The parser option string includes `n`, but usage/manpage do not document active no-write support; the code leaves it disabled.
- Online path is selected for any mounted filesystem after target validation; shrink validation rejects mounted shrink first.
