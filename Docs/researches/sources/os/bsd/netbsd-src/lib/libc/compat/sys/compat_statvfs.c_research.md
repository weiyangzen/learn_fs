# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statvfs.c

Read completely: 121 lines.

This implements compatibility `statvfs`, `statvfs1`, `fstatvfs`, `fstatvfs1`, and `getvfsstat` returning `statvfs90`. Single-object calls use `*190` current APIs and convert the result; `getvfsstat` allocates a native array, calls `__getvfsstat90`, converts each slot, and frees the array.

Security/reliability notes: `getvfsstat` calls `calloc(count, sizeof(*sb))` even when `buf` could conceptually be null; allocation size is derived from caller-provided `size`. Field narrowing is handled by `statvfs_to_statvfs90`.
