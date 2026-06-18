# File Research: sources/os/linux/linux/fs/xfs/scrub/attr_repair.h

This header exposes a narrow repair interface for extended attribute fork operations. It forward-declares `struct xrep_tempexch` and declares `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork`.

`xrep_xattr_swap` commits rebuilt tempfile attribute contents into the inode being repaired, either by direct local fork copy or by preparing both forks for an atomic mapping exchange. The reset helpers reap and reinitialize attr forks for the target inode or tempfile. These functions are used by xattr repair and by adjacent repair code that needs to clear corrupt attr fork state safely.
