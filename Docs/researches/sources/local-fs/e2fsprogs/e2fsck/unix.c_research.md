# File Research: sources/local-fs/e2fsprogs/e2fsck/unix.c

## Purpose
Unix command-line front end and main driver for e2fsck. It parses options, opens the device, enforces mount/MMP/journal safety, runs the checker, handles retries/restarts, writes repairs, and returns fsck-compatible exit codes.

## Main Elements
- Globals/options: `cflag`, `verbose`, bad-block mode flags, `e2fsck_global_ctx`, optional JBD debug.
- `usage()`: prints supported options and exits with `FSCK_USAGE`.
- `show_stats()`: emits compact or verbose filesystem usage, fragmentation, extent depth, and file-type counts.
- `check_mount()`: prevents unsafe writable checks of mounted or busy filesystems unless read-only/interactive policy permits.
- `is_on_batt()` and `check_if_skip()`: decide whether a clean filesystem can skip full checking based on state, mount count, intervals, battery, backup-super mismatch, and free count fixes.
- Progress support:
  - `calc_percent()`, `e2fsck_clear_progbar()`, `e2fsck_simple_progress()`, `e2fsck_update_progress()`.
  - `SIGUSR1` enables progress, `SIGUSR2` disables it, `SIGINT`/`SIGTERM` request cancellation.
- `parse_extended_opts()`: handles `-E` options including `ea_ver`, readahead, journal-only, discard, extent optimization, full inode count maps, logging, bmap-to-extent, fixes-only, unshare, and encoding checks.
- `PRS()`: allocates context, parses CLI/config, validates mutually exclusive modes, resolves devices, sets signals, logging/profiles, read-only behavior, readahead, badblocks PATH, and debug options.
- `try_open_fs()`: opens ext filesystems, trying block sizes for explicit superblocks and setting bitmap defaults.
- `e2fsck_check_mmp()`: validates multiple-mount-protection state and reports or clears invalid MMP conditions.
- `e2fsck_setup_tdb()`: configures undo I/O backing via explicit undo file or configured undo directory.
- `main()`: complete lifecycle from diagnostics and NLS setup through open/retry/recovery/check/final flush/cleanup.

## Control Flow
`main()` installs crash handling, initializes locale and error tables, parses arguments, verifies mount safety, opens the filesystem with proper flags, optionally tries backup superblocks or relaxed open flags, checks device size, handles MMP restart, validates/replays journal, rejects unsupported features, runs `check_super_block()`, optional bad block scan/import, reads bad block inode, initializes quotas, runs `e2fsck_run()`, recreates journal/orphan file if needed, updates quotas, handles checker restart requests, writes bitmaps and superblock changes, prints stats/resources, and exits with fsck status bits.

## Dependencies And Integration
This is the top-level e2fsck executable entry point. It integrates libext2fs I/O managers, undo I/O, blkid/devname resolution, profiles, problem handling, quota code, journal recovery, badblocks support, resource tracking, NLS, MMP, and the pass engine `e2fsck_run()`.

## Risk Notes
The file contains most safety gates for mounted filesystems, read-only mode, exclusive opens, MMP, and journal recovery. Bugs here can cause either dangerous checks on active devices or refusal to repair valid cases. Restart paths are complex because journal replay, MMP enabling, floppy-style exclusive opens, backup superblocks, and checker-requested restarts all loop through `restart`.
