# sources/user-network-fs/nfs-utils/systemd/rpc-statd-notify.service

Purpose: This unit runs `sm-notify` to tell NFS peers that the local system restarted.

Important APIs and control flow: It disables default dependencies, starts after local filesystems, network-online, name service lookup, and `nfs-server.service`, is `PartOf=nfs-utils.service`, and runs `-/usr/sbin/sm-notify` as a forking service with `RemainAfterExit=yes`. The leading dash makes failures non-fatal to systemd.

State, dependencies, and integration: It consumes NSM notify records and works with rpc.statd state. Ordering after nfs-server ensures clients are not notified before the server is available.

Risks and test signals: Failure is ignored, which can hide notification problems. Tests should simulate pending `sm.bak` records, network unavailable, server-enabled ordering, and restart idempotence.
