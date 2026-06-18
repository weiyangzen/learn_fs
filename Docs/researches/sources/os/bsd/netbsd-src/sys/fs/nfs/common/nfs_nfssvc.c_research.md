# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfs_nfssvc.c

This file implements the `nfssvc(2)` syscall dispatcher module.

Key contents:
- Registers the `nfssvc` syscall at `SYS_nfssvc` on module load and deregisters it on unload.
- Exposes dispatch function pointers: `nfsd_call_nfsserver`, `nfsd_call_nfscommon`, `nfsd_call_nfscl`, and `nfsd_call_nfsd`.
- `sys_nfssvc()` audits the command flag, allows unprivileged stats retrieval, and requires `PRIV_NFS_DAEMON` for other operations.
- Dispatches flag groups to the registered server, client callback daemon, common, or nfsd module handlers.
- Converts `EINTR`/`ERESTART` returns to success for syscall behavior.
- Unload refuses with `EBUSY` while any module dispatch hook remains installed.

Important dependencies:
- Other modules register by setting the global function pointers.
- Common handling is provided by `nfs_commonport.c`.

Risks and notes:
- Dispatch depends entirely on flag grouping; adding a new `NFSSVC_*` flag requires updating this router and the target module.
