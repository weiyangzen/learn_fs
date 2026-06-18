# File Research: sources/os/linux/linux/fs/orangefs/orangefs-sysfs.c

Implements OrangeFS sysfs ABI under `/sys/fs/orangefs`.

Key behavior:
- Provides local integer tunables for `op_timeout_secs`, `slot_timeout_secs`, `cache_timeout_msecs`, `dcache_timeout_msecs`, and `getattr_timeout_msecs`.
- Exposes local stats `reads` and `writes`.
- Uses service operations to get/set daemon-side parameters: performance history/time/reset, readahead count/size/count_size/readcnt, and cache hard/soft/reclaim/timeout settings for acache, capcache, ccache, and ncache.
- Exposes performance counter reads under `perf_counters` by issuing `ORANGEFS_VFS_OP_PERF_COUNT`.
- Blocks writes to `perf_counters` and `stats`.
- Rejects readahead sysfs operations when `ORANGEFS_FEATURE_READAHEAD` is not negotiated.
- Validates user input ranges before sending parameter set operations.
- Creates kobjects for `/sys/fs/orangefs`, `acache`, `capcache`, `ccache`, `ncache`, `perf_counters`, and `stats`, with cleanup through `kobject_put()`.

Notable details:
- All sysfs attributes route through a shared `orangefs_attribute` wrapper and dispatch to integer or service-operation show/store handlers.
- Many daemon-backed reads/writes fail if the userspace client is not in service.
