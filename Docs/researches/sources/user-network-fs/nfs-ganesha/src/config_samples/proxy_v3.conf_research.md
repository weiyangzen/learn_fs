<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf

Purpose: sample export that exposes a remote NFSv3 server through FSAL_PROXY_V3.

Important config surface: top-level `PROXY_V3 { num_sockets = 64; }` controls the proxy connection pool. The `EXPORT` maps remote `Path = /tmp` to local `Pseudo = /tmp_proxy`, uses RW access, `Squash = no_root_squash`, and `FSAL { Name = PROXY_V3; Srv_Addr = 10.0.0.3; }`.

Control flow/state: Ganesha receives client operations and forwards them to the configured remote server using pooled NFSv3 connections. Persistent file state remains on the upstream NFS server.

Dependencies/integration: requires FSAL_PROXY_V3 support and network reachability to `Srv_Addr`. The pseudo path still matters for Ganesha NFSv4 namespace even though the backend is NFSv3.

Risks: placeholder server address and `/tmp` path must be changed. `no_root_squash` and broad RW access are unsafe for untrusted clients. The socket pool size can stress upstream servers or limit concurrency if poorly tuned.

Test signals: point `Srv_Addr` at a real NFSv3 export, mount through Ganesha, and verify forwarded lookup/create/read/write behavior plus connection-pool behavior under concurrent load.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v3.conf -->
