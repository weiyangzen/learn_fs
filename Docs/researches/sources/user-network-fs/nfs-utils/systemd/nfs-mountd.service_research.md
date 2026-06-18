# sources/user-network-fs/nfs-utils/systemd/nfs-mountd.service

Purpose: This unit runs `rpc.mountd`, the NFS mount daemon used by the NFS server.

Important APIs and control flow: It has no default dependencies, requires `proc-fs-nfsd.mount`, wants network-online, starts after nfsd procfs, network/local filesystems, and rpcbind socket, and `BindsTo=nfs-server.service`. It runs `/usr/sbin/rpc.mountd` as a forking service.

State, dependencies, and integration: mountd depends on kernel nfsd state and export configuration. `BindsTo` ties its lifetime to `nfs-server.service`.

Risks and test signals: rpcbind ordering is `After` only, while `nfs-server.service` wants rpcbind.socket. Reexport configs may also require fsidd ordering. Tests should cover server start/stop, export reload, rpcbind unavailable, and shutdown ordering.
