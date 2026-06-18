# File Research: sources/os/linux/linux-stable/fs/cachefiles/Kconfig

This Kconfig file defines build-time options for the CacheFiles filesystem cache backend.

Configuration entries:
- `CACHEFILES`: tristate option for filesystem caching on files. It depends on `NETFS_SUPPORT`, `FSCACHE`, and `BLOCK`. The help text describes using a mounted local filesystem as a cache for other filesystems, primarily network filesystems.
- `CACHEFILES_DEBUG`: optional dynamic debug support for CacheFiles. It depends on `CACHEFILES` and enables runtime debug output via module parameter or cachefilesd configuration.
- `CACHEFILES_ERROR_INJECTION`: optional fault injection support. It depends on `CACHEFILES` and `SYSCTL`, enabling live error injection through sysctl while a cache is active.
- `CACHEFILES_ONDEMAND`: optional userspace-assisted on-demand read support. It depends on `CACHEFILES`, defaults to `n`, and changes miss handling so userspace fetches data for the cache backend instead of the netfs fetching directly.

The file establishes CacheFiles as an FS-Cache/netfs backend rather than a standalone filesystem. Optional modes map directly to extra compilation units in the Makefile: `error_inject.o` and `ondemand.o`.

Notable behavior implication:
- On-demand mode is explicitly opt-in and off by default, reflecting a larger userspace protocol and daemon responsibility surface.
