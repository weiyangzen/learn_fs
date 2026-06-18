# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfssvc.h

This header defines flag bits for the `nfssvc()` system call interface used to configure and run NFS server, client callback, stable-storage, identity-mapping, GSS, statistics, and diagnostic operations.

Key contents:
- Legacy service flags such as `NFSSVC_OLDNFSD`, `NFSSVC_ADDSOCK`, and `NFSSVC_NFSD`.
- NFSv4/newnfs service flags for public file handles, stable restart/backup, nfsd thread/socket setup, ID-name mapping, GSS daemon port management, nfsuserd port management, v4 root export, admin revoke, client/lock dumps, callback daemon/socket setup, stats retrieval/zeroing, nfsd suspend/resume, mount-option dump, and new-structure ABI.
- `struct nfscl_dumpmntopts`, used with `NFSSVC_DUMPMNTOPTS` to pass a filename, buffer length, and buffer pointer.

Important behavior:
- Several flags are operation selectors while others are modifiers, notably `NFSSVC_ZEROCLTSTATS` and `NFSSVC_ZEROSRVSTATS` for `NFSSVC_GETSTATS`.
- These constants form a user/kernel ABI, so bit changes affect mount tools, daemons, and diagnostic utilities.

Research notes:
- This is the syscall-control flag source for `nfs_nfssvc.c` and userland NFS management tools.
- Risk areas are ABI compatibility, flag collisions, and ensuring user-supplied buffers are handled according to the exact operation flag.
