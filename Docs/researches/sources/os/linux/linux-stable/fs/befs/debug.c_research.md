# File Research: sources/os/linux/linux-stable/fs/befs/debug.c

This file implements BeFS logging and optional structured debug dumping.

Logging functions:
- `befs_error()` prints `pr_err()` with the superblock id.
- `befs_warning()` prints `pr_warn()` with the superblock id.
- `befs_debug()` emits `pr_debug()` only under `CONFIG_BEFS_DEBUG`.

Debug dump functions:
- `befs_dump_inode()` prints on-disk inode fields, direct block runs, indirect metadata, datastream size, or symlink bytes.
- `befs_dump_super_block()` prints the on-disk superblock after endian conversion.
- `befs_dump_index_entry()` prints B+tree superblock fields.
- `befs_dump_index_node()` prints B+tree node header fields.
- Unused `befs_dump_small_data()` and `befs_dump_run()` are disabled under `#if 0`.

Integration:
- Called from `super.c`, `linuxvfs.c`, `btree.c`, `datastream.c`, `inode.c`, and `io.c`.
- Uses endian helpers, so dumps are meaningful for both little- and big-endian BeFS volumes.

Risk notes:
- Debug-only symlink dumping prints raw inline symlink bytes as a C string, relying on sane disk contents.
- Production logging is intentionally minimal; detailed metadata visibility requires `CONFIG_BEFS_DEBUG`.
