# sources/user-network-fs/nfs-utils/systemd/nfs-idmapd.service

Purpose: This unit runs `rpc.idmapd`, the NFSv4 ID-name mapping daemon.

Important APIs and control flow: It requires `rpc_pipefs.target`, starts after rpc_pipefs, local filesystems, and network-online, wants network-online, and is `PartOf=nfs-server.service`. It runs `/usr/sbin/rpc.idmapd` as a forking service.

State, dependencies, and integration: The daemon uses rpc_pipefs and idmap configuration/cache state. The unit is pulled into server workflows through `nfs-server.service` wants.

Risks and test signals: Being only `PartOf=nfs-server.service` means client-only activation depends on other targets not shown in this file. Tests should verify NFSv4 server startup pulls idmapd, rpc_pipefs ordering, restart propagation, and daemon failure behavior.
