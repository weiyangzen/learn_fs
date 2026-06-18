# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fgetln.c

Read completely: 64 lines.

This file implements `fgetln` by locking the stream and calling `__fgetstr(fp, lenp, '\n')`. The implementation now uses the shared `getdelim`-based helper, returning a NUL-terminated internal buffer while preserving `fgetln` length reporting.

Important interactions: weak alias `_fgetln`; depends on `fgetstr.c`.

Security/reliability notes: returned storage is stream-owned and overwritten by later line reads.
