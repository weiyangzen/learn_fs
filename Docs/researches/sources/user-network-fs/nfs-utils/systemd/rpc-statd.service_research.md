# sources/user-network-fs/nfs-utils/systemd/rpc-statd.service

Purpose: This unit runs `rpc.statd`, the NFSv2/v3 status monitor used for lock recovery.

Important APIs and control flow: It disables default dependencies, conflicts with unmount, requires name service lookup and rpcbind socket, wants network-online and statd-notify, starts after network, lookup, rpcbind service/socket, and is `PartOf=nfs-utils.service`. It sets `RPC_STATD_NO_NOTIFY=1`, runs as a forking service with `/run/rpc.statd.pid`.

State, dependencies, and integration: statd uses the NSM on-disk database and rpcbind registration. Notification is delegated to `rpc-statd-notify.service`.

Risks and test signals: Both `rpcbind.service` and socket ordering are present, but only socket is required. Tests should verify rpcbind activation, pidfile handling, no-notify environment behavior, restart propagation, and shutdown before unmount.
