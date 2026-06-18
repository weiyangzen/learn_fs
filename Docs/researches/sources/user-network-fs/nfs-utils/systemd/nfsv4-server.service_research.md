# sources/user-network-fs/nfs-utils/systemd/nfsv4-server.service

Purpose: `nfsv4-server.service` starts an NFSv4-only server stack.

Important APIs and control flow: It requires network target, `proc-fs-nfsd.mount`, and `nfsv4-exportd.service`; wants network-online, idmapd, nfsdcld, and auth-rpcgss. Startup refreshes exports and runs `rpc.nfsd -N 3`, disabling NFSv3; shutdown runs `rpc.nfsd 0` and flushes export state.

State, dependencies, and integration: It remains active as a oneshot and installs into `multi-user.target`. It integrates with kernel nfsd, exportfs, id mapping, client tracking, and GSS support.

Risks and test signals: GSS services are ordered after but only auth-rpcgss is wanted here. Tests should verify NFSv3 disabled, NFSv4 exports active, idmapd/nfsdcld ordering, stop cleanup, and coexistence conflict expectations with full `nfs-server.service`.
