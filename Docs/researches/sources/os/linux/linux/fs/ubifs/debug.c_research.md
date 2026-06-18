# File Research: sources/os/linux/linux/fs/ubifs/debug.c

Read completely: 3052 lines.

This file implements UBIFS debug-only dumping, consistency checking, power-cut fault injection, debugfs controls, and assertion handling.

Main responsibilities:
- Formats keys, node types, commit states, journal heads, inodes, nodes, lprops, budgeting state, LPT state, LEB scans, TNC znodes, heaps, pnodes, and the on-flash index.
- Saves and checks space-accounting snapshots.
- Checks synchronized inode sizes, directory size/link counts, TNC ordering and znode invariants, index size, full filesystem inode/link/xattr consistency, and scan-node ordering.
- Emulates power cuts around UBI LEB write/change/unmap/map operations and can corrupt a partial write buffer before returning `-EROFS`.
- Exposes per-mount and global debugfs knobs for extra checks, recovery testing, forced read-only error state, and dump triggers.
- Implements `ubifs_assert_failed` behavior for panic, read-only transition, or stack reporting.

Key APIs: `ubifs_dump_inode`, `ubifs_dump_node`, `ubifs_dump_lprops`, `ubifs_dump_budg`, `ubifs_dump_tnc`, `ubifs_dump_index`, `dbg_walk_index`, `dbg_check_tnc`, `dbg_check_idx_size`, `dbg_check_filesystem`, `dbg_check_space_info`, `dbg_leb_write`, `dbg_leb_change`, `dbg_leb_unmap`, `dbg_leb_map`, `dbg_debugfs_init_fs`, `dbg_debugfs_exit_fs`, `dbg_debugfs_init`, `dbg_debugfs_exit`, `ubifs_debugging_init`, and `ubifs_debugging_exit`.

Important behavior: node dumping is defensive about bad magic, unknown types, truncated lengths, and invalid name lengths. TNC checking verifies parent/child relationships, dirty-parent ordering, key ranges, duplicate/colliding key order, and clean/dirty znode counters. Full filesystem checking walks the index, reads all leaf nodes, builds an RB-tree of inode facts, and compares stored inode link/xattr/size metadata against calculated references.

Important interactions: this file is called from many UBIFS subsystems through `dbg_*` helpers and wraps low-level UBI I/O when recovery testing is enabled. It depends on TNC, LPT/lprops, budgeting, scan, journal, xattr, and VFS inode state being internally coherent.

Reliability notes: debug checks are intentionally heavyweight and normally gated by global/per-mount flags. Fault injection can intentionally corrupt data and force `-EROFS`; it must remain confined to recovery testing. Debugfs knobs are writable by root and can trigger expensive dumps or force `c->ro_error`.
