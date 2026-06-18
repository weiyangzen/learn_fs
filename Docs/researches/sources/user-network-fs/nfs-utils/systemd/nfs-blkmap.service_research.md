# sources/user-network-fs/nfs-utils/systemd/nfs-blkmap.service

Purpose: This service runs `blkmapd`, the pNFS block layout mapping daemon.

Important APIs and control flow: It disables default dependencies, conflicts with shutdown unmount, requires and starts after `rpc_pipefs.target`, is `PartOf=nfs-utils.service`, and runs as a forking service with `/run/blkmapd.pid`.

State, dependencies, and integration: It depends on rpc_pipefs being mounted and participates in the broader NFS client service group. The daemon persists runtime state in its own pidfile and kernel/rpc_pipefs interactions.

Risks and test signals: Forking/pidfile assumptions must match daemon behavior. Missing rpc_pipefs blocks service startup. Tests should start/stop with `nfs-client.target`, restart `nfs-utils.service`, and verify clean shutdown ordering before unmount.
