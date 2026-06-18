# sources/user-network-fs/nfs-utils/systemd/nfsv4-exportd.service

Purpose: This unit runs `nfsv4.exportd`, the NFSv4-only mount/export daemon.

Important APIs and control flow: It requires `proc-fs-nfsd.mount`, wants network-online, starts after nfsd procfs, network-online, and local filesystems, and `BindsTo=nfsv4-server.service`. It runs `/usr/sbin/nfsv4.exportd` as a forking service.

State, dependencies, and integration: It is tied to `nfsv4-server.service` and kernel nfsd procfs, serving export information for an NFSv4-only server mode.

Risks and test signals: There is no install section here, so the v4 server unit is the activation path. Tests should start/stop `nfsv4-server.service`, verify export daemon binding, and exercise network-online delays.
