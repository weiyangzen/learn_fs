# sources/user-network-fs/nfs-utils/support/misc/xstat.c

Purpose: stat wrappers that prefer non-synchronizing `statx()` metadata queries when available and fall back to `fstatat()`, `lstat()`, or `stat()`.

Important APIs and functions: `xlstat()` is lstat-like with `AT_SYMLINK_NOFOLLOW`; `xstat()` is stat-like. `statx_copy()` maps `struct statx` fields into `struct stat`, and `statx_do_stat()` disables future `statx()` attempts after `ENOSYS`.

Control flow: with `HAVE_FSTATAT`, calls first try `statx(..., STATX_BASIC_STATS, AT_STATX_DONT_SYNC | AT_NO_AUTOMOUNT...)`. If unsupported, errno is reset and `fstatat()` is used. Without `HAVE_FSTATAT`, the wrappers directly call libc `lstat()` and `stat()`.

State and persistence: only a static `statx_supported` flag caches kernel/libc support. No persistent state.

Dependencies and integration: depends on Linux statx headers when configured, `sysmacros.h`, `nfslib.h` for `UNUSED`, and `xstat.h`. It is used by code that wants metadata without triggering automounts or remote sync where possible.

Risks: the fallback behavior depends heavily on configure-time feature detection. `statx_copy()` maps only basic fields and ignores birth time, attributes, and masks. Static `statx_supported` is process-global and not synchronized, though the benign race only affects fallback selection.

Test signals: verify symlink and non-symlink paths, automount boundaries, kernels with and without `statx`, `EINVAL` emulation behavior, and parity of key `struct stat` fields.
