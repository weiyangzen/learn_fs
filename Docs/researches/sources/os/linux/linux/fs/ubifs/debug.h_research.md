# File Research: sources/os/linux/linux/fs/ubifs/debug.h

Read completely: 305 lines.

This header declares UBIFS debug data structures, debug message macros, assertion helpers, check enablement helpers, dump/check APIs, fault-injection UBI wrappers, and debugfs lifecycle functions.

Main contents:
- `struct ubifs_debug_info`, the per-filesystem debug state for saved old index roots, emulated power-cut state, LPT size-check state, saved budgeting/lprops snapshots, per-mount check flags, recovery-test flag, and debugfs dentries.
- `struct ubifs_global_debug_info`, the global check/recovery-test switches.
- `ubifs_assert`, `ubifs_assert_cmt_locked`, and categorized `dbg_*` logging macros.
- Inline helpers such as `dbg_is_chk_gen`, `dbg_is_chk_index`, `dbg_is_chk_fs`, `dbg_is_tst_rcvry`, and `dbg_is_power_cut`.
- Prototypes for all dumpers, checkers, index walking, LEB wrappers, and debugfs init/exit functions.

Important interactions: most UBIFS files include this through `ubifs.h` and use the macros as low-cost gates around optional validation. `debug.c` provides the backing storage and implementations.

Reliability notes: when debug support is active, assertion action is runtime-controlled by `c->assert_action`. The check-enable helpers combine global and per-mount flags, so enabling a global debugfs knob affects all UBIFS mounts.
