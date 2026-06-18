# File Research: sources/os/linux/linux-stable/fs/ubifs/debug.h

UBIFS debug declarations, debug state structures, message macros, checker gates, and debugfs API prototypes.

Key responsibilities:
- Defines `struct ubifs_debug_info`, the per-mount debug state.
- Defines `struct ubifs_global_debug_info`, the global debug flags inherited/combined with per-mount flags.
- Provides `ubifs_assert()` and `ubifs_assert_cmt_locked()` helpers.
- Defines debug message macros by subsystem: general, journal, TNC, lprops, find, mount, I/O, commit, budgeting, log, GC, scan, and recovery.
- Declares dump, walk, checker, recovery-test LEB wrappers, and debugfs lifecycle functions.

Important fields in `ubifs_debug_info`:
- Old index root snapshot for old-index checking.
- Power-cut emulation state: happened flag, delay mode, timeout, call count, and max calls.
- LPT checking scratch state and saved space/budget snapshots.
- Per-mount boolean gates for general, index, orphan, lprops, filesystem, and recovery testing checks.
- Debugfs dentries for dump files, checker knobs, recovery testing, and forced read-only error.

Important behavior:
- `dbg_is_chk_*()` and `dbg_is_tst_rcvry()` OR global and per-FS settings.
- `dbg_is_power_cut()` checks whether a recovery-test fault has already happened.
- `DBG_KEY_BUF_LEN` centralizes short debug key formatting buffers.

Cross-file links:
- Implemented mostly by `debug.c`.
- Used throughout UBIFS to keep debug checks cheap when disabled.
- The LEB wrapper prototypes are used by lower-level I/O paths when debug recovery testing is compiled/enabled.

Invariants and risks:
- `c->dbg` must exist before any debug helper dereferences per-FS debug flags.
- Debug macros compile to `pr_debug()` style messages and rely on UBIFS key formatting helpers.
- Assertion behavior is implemented in `debug.c` and can report, force read-only mode, or panic depending on mount/module configuration.
