<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf -->
## sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf

Purpose: sample export that proxies a remote NFSv4 server through FSAL_PROXY_V4.

Important config surface: one `EXPORT` with id `77`, remote `Path = /tmp`, local `Pseudo = /tmp_proxy`, RW access, `Squash = no_root_squash`, and `FSAL { Name = PROXY_V4; Srv_Addr = 10.0.0.3; Use_Privileged_Client_Port = true; }`.

Control flow/state: Ganesha handles client requests and relays file operations/state to the upstream NFSv4 server. Persistent state is owned by the remote server; Ganesha also participates in NFSv4 client/session/state mediation.

Dependencies/integration: requires FSAL_PROXY_V4 and network connectivity to the upstream NFSv4 service. `Use_Privileged_Client_Port` integrates with upstream exports that trust privileged source ports.

Risks: privileged client ports can be required by legacy security policy but are not a complete security boundary. Placeholder address/path must be replaced. Root-unsquashed RW proxying can amplify misconfiguration against the upstream export.

Test signals: configure a real upstream NFSv4 target, mount the Ganesha pseudo path, and validate stateful operations such as open, close, locks, and recovery behavior in addition to basic I/O.
<!-- END_FILE_RESEARCH: sources/user-network-fs/nfs-ganesha/src/config_samples/proxy_v4.conf -->
