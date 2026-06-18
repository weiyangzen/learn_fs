# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs.h

Primary shared header for `unsquashfs` and version-specific unsquash readers.

Defines:
- Common includes, `TRUE`/`FALSE`, `TABLE_HASH()`, and `MAXIMUM_READ_SIZE`.
- Unified `struct super_block` containing Squashfs v4 fields plus legacy uid/gid fields.
- In-memory normalized inode model: block list location, data size, fragment metadata, uid/gid/mode/time/type, symlink target, sparse flag, and xattr index.
- `squashfs_operations`, the dispatch table used by `unsquashfs.c` to support multiple Squashfs on-disk versions.
- Directory, queue, cache, file-entry, path-filter, path-stack, and directory-loop/hardlink lookup structures.
- Path matching constants for exact/wildcard/regex and extract/exclude/link nodes.
- Bit-table macros for directory loop detection and lookup table macros for hard-link resolution.

Exports:
- Global extraction state used by helper modules.
- Core read/write/progress/debug helpers from `unsquashfs.c`.
- Version-reader entry points from `unsquash-1.c`, `unsquash-2.c`, `unsquash-3.c`, `unsquash-4.c`, and shared helpers from `unsquash-123*.c`.
- Date parsing hook `exec_date()`.

This header is the ABI glue between the generic extraction engine and Squashfs-version-specific metadata decoders.
