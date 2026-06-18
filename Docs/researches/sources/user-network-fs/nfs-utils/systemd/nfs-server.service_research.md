# sources/user-network-fs/nfs-utils/systemd/nfs-server.service

Purpose: `nfs-server.service` orchestrates full NFS server startup and shutdown.

Important APIs and control flow: It requires network target, `proc-fs-nfsd.mount`, and `nfs-mountd.service`; wants rpcbind, network-online, statd, idmapd, statd-notify, nfsdcld, auth-rpcgss, and svcgssd. Startup refreshes exports, then runs `nfsdctl autostart` or falls back to `rpc.nfsd`; shutdown sets nfsd threads to zero or falls back to `rpc.nfsd 0`, then unexports and flushes exportfs state.

State, dependencies, and integration: It leaves oneshot state active and is installed for `multi-user.target`. Kernel nfsd state, export tables, rpcbind, GSS services, and client tracking are integration points.

Risks and test signals: Several dependencies are wants, so missing helpers may not fail the server unit. Shell fallback behavior must be tested with and without `nfsdctl`. Tests should cover start, reload, stop, partial dependency failures, and export cleanup.
