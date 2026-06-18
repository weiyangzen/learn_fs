# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mount.c

Read completely: 27 lines.

This implements old `mount`, forwarding to `__mount50(type, dir, flags, data, 0)`. It discards positive return values, returning `0` for all non-`-1` results.

Important interactions: length `0` tells the kernel to use the default filesystem argument size.

Security/reliability notes: intentionally erases positive `MNT_GETARGS`-style responses for old ABI behavior.
