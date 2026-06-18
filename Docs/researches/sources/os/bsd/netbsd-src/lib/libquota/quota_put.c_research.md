# File Research: sources/os/bsd/netbsd-src/lib/libquota/quota_put.c

This file implements the public `quota_put` operation as a backend dispatcher. NFS handles return `EOPNOTSUPP` because the rquota backend is read-only. Old quota-file handles call `__quota_oldfiles_put`, and kernel handles call `__quota_kernel_put`.

Unknown handle modes return `EINVAL`. All actual storage semantics, including old quota-file record merging and kernel `QUOTACTL_PUT`, live in the backend files.
