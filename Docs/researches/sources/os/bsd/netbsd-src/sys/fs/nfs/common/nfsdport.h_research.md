# File Research: sources/os/bsd/netbsd-src/sys/fs/nfs/common/nfsdport.h

This header provides server-side porting macros and small abstractions for the common NFS server code.

Key contents:
- Defines `NFSVNO_*` macros for initializing, setting, unsetting, and testing `nfsvattr` fields.
- Defines `struct nfsexstuff`, which carries export flags and security flavors returned by file-handle-to-vnode lookup.
- Defines `NFSEXITCODE()` and `NFSEXITCODE2()` as no-ops in this port.
- Defines export flag query/set macros such as `NFSVNO_EXPORTED()`, `NFSVNO_EXRDONLY()`, and `NFSVNO_EXV4ONLY()`.
- Defines file-handle comparison, lock hash, file pointer, and namei component setup macros.
- Provides small Darwin KPI compatibility aliases for `vnode_mount()` and `vfs_statfs()`.
- Defines server file-handle min/max sizes as `sizeof(fhandle_t)`.
- Provides `NFSD_DEBUG()` gated by `nfsd_debuglevel`.

Important dependencies:
- Used by server vnode-port and common server code.
- Bridges imported FreeBSD/Darwin-oriented code to NetBSD vnode/export conventions.

Risks and notes:
- Many macros hide direct structure field access, so type/field changes in NetBSD vnode/export structures would require updates here.
