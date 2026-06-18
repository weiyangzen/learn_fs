# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs_sys.c

## Purpose
Implements the `nfssys` system-call dispatcher and related exported entry points for NFS kernel control operations initiated by userland daemons and administrative tools.

## Key Elements
`nfs_export` copies in `exportfs_args` using the caller data model and calls `exportfs`. `nfssys` switches on `enum nfssys_op`, applies `secpolicy_nfs` to privileged operations except `NFS_REVAUTH` and `NFS4_SVC`, copies in data-model-aware argument structures, and dispatches to NFS, RPC, lock manager, logging, idmap, mountd, and nfscmd subsystems.

Handled operations include NFSv4 client state clearing, RPC service pool create/wait/run, RDMA NFS service startup, NFS server daemon entry, exportfs, filehandle lookup, credential revocation, lock manager service/shutdown, NFS log flush, NFSv4 callback service, NFSv4 server quiesce registration, idmap argument delivery, distributed stable storage path delivery, ephemeral mount timeout setting, mountd door argument passing, and nfscmd door argument passing.

Global hooks such as `nfs_srv_quiesce_func` and `nfs_srv_dss_func` are filled by the server module when loaded. `rfs4_lease_time`, `rfs4_grace_period`, and `nfs4_dss_buflen` provide shared NFSv4 server/control state.

## Dependencies
Uses illumos syscall copyin/datamodel support, credential policy checks, RPC service pool APIs, NFS server/client/lock/log/idmap/export helpers, RDMA service startup, kernel memory allocation, and function pointers supplied by the `nfssrv` module.

## Behavior/Risks
This is a privilege and ABI boundary. Every case must copy in the correct structure layout for native and non-native data models and return errors through `set_errno`. Some operations rely on call ordering, such as `NFS4_DSS_SETPATHS_SIZE` before `NFS4_DSS_SETPATHS`, and module-loaded hooks return `ENOTSUP` when unavailable. Expanding this switch requires careful policy decisions because a missing privilege gate could expose server-control operations to unprivileged callers.
