# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/stdlib/compat_unsetenv.c

Read completely: 86 lines.

This implements old `unsetenv` returning `void`. It locks the environment, repeatedly finds matching slots with `__getenvslot`, shifts `environ` entries left to delete every match, then unlocks.

Important interactions: uses current libc environment lock helpers and global `environ`.

Security/reliability notes: no error is returned to legacy callers. The environment lock protects concurrent libc environment access; callers still must avoid racing direct writes to `environ`.
