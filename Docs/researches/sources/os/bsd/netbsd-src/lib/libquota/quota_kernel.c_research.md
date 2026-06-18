# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_kernel.c

This file implements the modern kernel quota backend by wrapping `__quotactl` operations. `__quota_kernel_stat` issues `QUOTACTL_STAT` and underlies implementation-name, restriction, id-type count, and object-type count queries. Type-name and object-type detail functions issue `QUOTACTL_IDTYPESTAT` and `QUOTACTL_OBJTYPESTAT`.

`__quota_kernel_quotaon` fetches the oldfiles quota filename from fstab data and passes it to `QUOTACTL_QUOTAON`. Its comment explains that filesystems decide whether quotaon is valid and that repeated quotaon is allowed. `__quota_kernel_quotaoff` issues `QUOTACTL_QUOTAOFF`.

Data operations are straightforward: `__quota_kernel_get` uses `QUOTACTL_GET`, `put` uses `QUOTACTL_PUT`, and `delete` uses `QUOTACTL_DEL`, all keyed by the mountpoint stored in the quota handle.

Kernel cursors are thin wrappers around `struct quotakcursor`. Create opens with `QUOTACTL_CURSOROPEN`; destroy sends `QUOTACTL_CURSORCLOSE` and warns if that fails; skip, get, atend, and rewind map to the corresponding cursor quotactl operations. `cursor_getn` rejects `maxnum > INT_MAX`, returns the kernel-reported number of entries, and `cursor_get` simply asks for one entry. `cursor_atend` returns -1 on kernel error so simple nonzero tests stop iterating while advanced callers can distinguish errors.
