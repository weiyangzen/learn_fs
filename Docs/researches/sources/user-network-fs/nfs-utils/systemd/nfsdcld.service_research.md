# sources/user-network-fs/nfs-utils/systemd/nfsdcld.service

Purpose: This unit runs `nfsdcld`, the NFSv4 client tracking daemon for server-side lease recovery.

Important APIs and control flow: It disables default dependencies, conflicts with unmount, requires rpc_pipefs and `proc-fs-nfsd.mount`, starts after those plus `systemd-remount-fs.service`, and runs `/usr/sbin/nfsdcld` as a forking service.

State, dependencies, and integration: nfsdcld persists client tracking data and communicates through kernel nfsd/rpc_pipefs interfaces. It is wanted by server units.

Risks and test signals: The unit has no install section here, so activation depends on wants from server services. Tests should validate server startup pulls it in, client tracking database availability, restart behavior, and shutdown before unmount.
