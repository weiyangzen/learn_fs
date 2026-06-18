# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_msync.c

Read completely: 48 lines.

This implements old two-argument `msync`. It calls `__msync13(addr, size, MS_SYNC | MS_INVALIDATE)`.

Security/reliability notes: hard-codes historical sync/invalidate behavior; no local validation.
