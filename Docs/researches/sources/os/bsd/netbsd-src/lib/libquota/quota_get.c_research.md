# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_get.c

This file provides `quotaval_clear` and the public `quota_get` dispatcher. `quotaval_clear` sets hard and soft limits to `QUOTA_NOLIMIT`, usage to zero, and both expire and grace time to `QUOTA_NOTIME`, establishing the library's representation for "no quota".

`quota_get` routes by `qh_mode`: NFS handles use `__quota_nfs_get`, old quota-file handles use `__quota_oldfiles_get`, and kernel handles use `__quota_kernel_get`. Unknown modes return `EINVAL`.

The file intentionally keeps common API behavior thin and leaves backend-specific validation, scaling, and error translation to the selected implementation.
