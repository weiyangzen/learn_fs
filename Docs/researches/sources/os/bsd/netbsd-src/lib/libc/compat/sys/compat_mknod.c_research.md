# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_mknod.c

Read completely: 59 lines.

This implements old `mknod` with a 32-bit device argument. It aliases `mknod` to `__compat_mknod` and forwards to `__mknod50`.

Security/reliability notes: device number width is constrained by the old ABI.
