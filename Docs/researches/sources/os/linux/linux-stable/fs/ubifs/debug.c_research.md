# File Research: sources/os/linux/linux-stable/fs/ubifs/debug.c

Large UBIFS debug implementation covering dump helpers, consistency checkers, power-cut emulation, debugfs controls, and assertion handling.

Key responsibilities:
- Human-readable formatting for keys, node types, dent types, commit states, and journal heads.
- Dump routines for in-memory and on-flash structures: inodes, nodes, budgeting state, LEB properties, LPT state, LEB contents, znodes, heaps, pnodes, TNC, and on-flash index.
- Consistency checkers for space accounting, synced inode size, directory size/link count, TNC ordering/shape, index size, full filesystem content, and scan-node order.
- Debug power-cut/fault injection wrappers around UBI LEB operations.
- Per-mount and global debugfs knobs for check categories, recovery testing, dumping, and forced `ro_error`.
- `ubifs_assert_failed()` behavior based on `assert_action`.

Major routines:
- `ubifs_dump_node()` safely decodes every UBIFS node type after checking magic, node type, and bounded node length.
- `dbg_check_tnc()` walks in-memory TNC znodes and validates parent/child relationships, key ordering, dirty-parent propagation, branch location fields, and optional clean/dirty znode counters.
- `dbg_walk_index()` loads missing znodes and traverses the on-flash index in postorder, invoking leaf and znode callbacks.
- `dbg_check_filesystem()` walks all index leaves, reads nodes, builds an RB-tree of inode accounting, then checks nlink, directory size, xattr size/count/name totals, and data-node bounds.
- `power_cut_emulated()` probabilistically injects failures with different odds for superblock, master, log, LPT, orphan, index-head, GC-head, bud, and non-bud LEBs.
- `dbg_leb_write()`, `dbg_leb_change()`, `dbg_leb_unmap()`, and `dbg_leb_map()` wrap UBI operations and return `-EROFS` after an emulated power cut.

Debugfs surface:
- Per-filesystem directory name follows `ubi%d_%d`.
- Per-FS files include `dump_lprops`, `dump_budg`, `dump_tnc`, `chk_general`, `chk_index`, `chk_orphans`, `chk_lprops`, `chk_fs`, `tst_recovery`, and `ro_error`.
- Global files under `ubifs` control default debug flags for all mounts.
- Boolean debugfs writes accept only leading `1` or `0`.

Cross-file links:
- `debug.h` declares the state, debug macros, and all public checker/dump entry points.
- `dir.c`, `file.c`, `find.c`, and other UBIFS subsystems call checker and dump helpers under debug gates.
- UBI access wrappers are substitutes for normal low-level LEB operations when recovery testing is enabled.

Invariants and risks:
- Many checkers are gated by `dbg_is_chk_*()` to avoid production overhead.
- `dbg_walk_index()` mutates/load-fills TNC state while walking, so it holds `tnc_mutex`.
- Full filesystem checking is intentionally heavyweight and reads the whole index plus referenced leaves.
- Power-cut testing deliberately corrupts buffers and transitions later operations to `-EROFS`; it is debug-only fault injection, not normal I/O behavior.
