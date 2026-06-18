# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/sys/compat_lfs_segwait.c

Read completely: 64 lines.

This implements old `lfs_segwait`, converting an optional `timeval50` timeout to native `timeval` and calling `__lfs_segwait50`.

Security/reliability notes: direct timeout conversion wrapper for LFS segment wait.
