# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/server/nfs_nfsdmodule.c

Minimal NetBSD module wrapper declaring `nfs_server` as a miscellaneous module depending on `nfs_common`. Its `nfs_server_modcmd()` accepts init and fini commands and returns `ENOTTY` for unknown module commands.

The file contains no server implementation; real NFS server load/unload behavior for this code group lives in `nfs_nfsdport.c`'s `nfsd_modevent()`.
