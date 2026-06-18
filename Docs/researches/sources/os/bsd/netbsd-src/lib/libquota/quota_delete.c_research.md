# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_delete.c

This file implements the public `quota_delete` operation as a mode dispatcher. It rejects NFS handles with `EOPNOTSUPP`, because rquotad access is read-only in this library. Old quota-file handles call `__quota_oldfiles_delete`, and kernel handles call `__quota_kernel_delete`.

If the handle contains an unknown mode, the function sets `EINVAL` and returns -1. The file contains no policy beyond backend selection; actual deletion semantics are implemented by clearing old quota-file records or issuing a kernel `QUOTACTL_DEL` request.
