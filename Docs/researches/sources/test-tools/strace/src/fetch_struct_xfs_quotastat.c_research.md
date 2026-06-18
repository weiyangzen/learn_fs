# sources/test-tools/strace/src/fetch_struct_xfs_quotastat.c

Mpers fetcher for XFS quota status structures from `<linux/dqblk_xfs.h>`. It copies tracee `fs_quota_stat_t` into the destination representation for XFS quota ioctl decoding. State is limited to fetched structure contents. Dependencies are mpers macros and XFS quota kernel headers. Risks are kernel header/layout drift and compat word-size differences in quota counters or timers. Tests should cover XFS quota status ioctls under native and compat builds, bad pointers, and representative nonzero quota fields.
