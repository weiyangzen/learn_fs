# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/jfs_compat.h

Provides userspace compatibility definitions so JBD/JBD2-derived journal code can compile inside e2fsprogs. It maps kernel-style endian helpers, allocation flags, logging macros, CRC helpers, spinlocks, and buffer-head conventions onto libext2fs equivalents or no-op stubs.

Defines the userspace `journal_s` structure used by journal replay/creation code, including superblock pointers, block ranges, transaction sequence fields, revoke tables, checksum seed, and fast-commit replay callback.

This header is intentionally not a full kernel emulation layer. Many kernel concepts are reduced to constants or no-ops, so code using it must not assume real locking, GFP behavior, or kernel logging semantics.
