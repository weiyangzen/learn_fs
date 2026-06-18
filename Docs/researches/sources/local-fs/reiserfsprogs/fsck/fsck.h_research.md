# File Research: sources/local-fs/reiserfsprogs/fsck/fsck.h

Shared header for `reiserfsck`.

Defines:
- Exit codes.
- Fsck modes: check, fix-fixable, rebuild superblock, rebuild tree, rollback, clean attributes, auto.
- Option flags: interactive, adjust-size, quiet, silent, background, skip journal, hash-defined, pass dump, rollback, yes, badblocks, force.
- Cross-pass function prototypes for pass0/pass1/pass2/semantic/lost+found/pass4, tree checking, bitmap allocation, objectid maps, rollback, and superblock rebuild.
- Rebuild/check statistics structures.
- `struct rebuild_info`, `struct check_info`, and `struct fsck_data`, stored in `fs->fs_vp`.
- Convenience macros for accessing pass stats, bitmaps, mode/options, logs, progress streams, and objectid maps.

Important shared state:
- Rebuild uses source/new/allocable/uninsertable bitmaps.
- Check uses corruption counters plus a deallocation bitmap.
- Objectid maps track proper and semantic allocation/relocation state.
- Progress output may go to stderr or `fsck.run`.

Macros:
- `fsck_log` suppresses messages under `OPT_SILENT`.
- `fsck_progress` writes and flushes progress output.
- `fsck_exit` reports and exits with user error.

Key role: central contract tying all fsck passes and main orchestration together.
