# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_cursor.c

This file implements the public quota cursor API and dispatches cursor operations to either legacy quota files or the kernel interface. NFS mode does not support cursors and returns `EOPNOTSUPP`.

`quota_opencursor` chooses restrictions based on the handle mode. Old files always require quotacheck-style access; kernel mode queries restrictions with `__quota_kernel_getrestrictions`. If restrictions include `QUOTA_RESTRICT_NEEDSQUOTACHECK` and old files are not already open, it initializes the old-file backend. It then allocates `struct quotacursor`, stores the handle, selects `QC_OLDFILES` or `QC_KERNEL`, and creates the backend cursor, preserving errno on allocation/creation failures.

`quotacursor_close` destroys the backend cursor and frees the wrapper. `quotacursor_skipidtype`, `quotacursor_get`, `quotacursor_getn`, `quotacursor_atend`, and `quotacursor_rewind` switch on `qc_type` and call the corresponding oldfiles or kernel helper. Any impossible cursor type falls through to `EINVAL`.

The design lets callers use one cursor API regardless of whether the mounted filesystem has a modern kernel quota iterator or must be scanned through quota1 files.
