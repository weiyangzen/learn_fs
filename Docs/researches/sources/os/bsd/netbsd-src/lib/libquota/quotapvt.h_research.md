# File Research: sources/os/bsd/netbsd-src/lib/libquota/quotapvt.h

This private libquota header defines backend mode constants, internal handle/cursor structures, and backend function prototypes. `QUOTA_MODE_NFS`, `QUOTA_MODE_OLDFILES`, and `QUOTA_MODE_KERNEL` identify the selected implementation.

`struct quotahandle` stores the mountpoint, mount device, mode, and oldfiles-only state: whether files are open and user/group quota file descriptors. `struct quotacursor` stores the owning handle, cursor type (`QC_OLDFILES` or `QC_KERNEL`), and a union of backend cursor pointers.

The prototypes are grouped by backend. Kernel functions expose implementation metadata, restrictions, id/object type info, quotaon/off, get/put/delete, and cursor operations. The NFS interface only exposes get. Oldfiles functions include fstab loading/lookup, initialization, implementation name, quota-file discovery, quotaon, get/put/delete, and cursor operations. The header also declares `__quota_getquota` compatibility for the old library interface.
