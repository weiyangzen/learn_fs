# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_statfs.c

Read completely: 124 lines.

This implements obsolete `statfs`, `fstatfs`, `fhstatfs`, and `getfsstat` by using current statvfs APIs and converting to `statfs12`. `getfsstat` allocates a temporary native statvfs array sized from the old buffer length, calls `__getvfsstat90`, and converts each returned entry.

Important interactions: warns callers to use statvfs/getvfsstat instead.

Security/reliability notes: `getfsstat` computes allocation size from caller-provided byte size; very large sizes could request large allocations. Conversion may narrow filesystem counters and flags to the old layout.
