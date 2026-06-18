# File Research: sources/os/linux/linux/fs/netfs/internal.h

Central private header for Linux netfs and FS-Cache implementation files.

Major contents:
- Includes core kernel, netfs, fscache, and trace headers.
- Declares internal APIs across buffered read/write, misc helpers, object lifetime, read/write collectors, retry paths, stats, fscache cache/cookie/volume/main/proc.
- Defines proc list helpers for active netfs I/O requests.
- Provides statistic increment/decrement wrappers gated by config options.
- Provides cache state helpers with acquire/release semantics.
- Provides request/subrequest in-progress tests with memory barriers.
- Provides netfs group reference helpers.
- Defines debug logging macros and assertion macros.

Important contracts:
- `netfs_check_rreq_in_progress()` and `netfs_check_subreq_in_progress()` impose ordering for collectors.
- `netfs_wake_rreq_flag()` clears request flags with unlock semantics and wakes waiters.
- `netfs_is_cache_enabled()` gates cache use on valid cookie, backend private state, and enabled cookie.
- FS-Cache config stubs make callers compile when `CONFIG_FSCACHE` or stats/proc config is disabled.

Role in architecture:
- This header ties together the state machines in this group: fscache cookie/volume state, netfs I/O request lifetime, collector/retry paths, and proc/stat visibility.
