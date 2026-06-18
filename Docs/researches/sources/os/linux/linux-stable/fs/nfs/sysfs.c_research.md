# File Research: sources/os/linux/linux-stable/fs/nfs/sysfs.c

Purpose: Implements NFS sysfs objects for global NFS, per-network-namespace NFS client state, and per-server controls/metadata.

Key responsibilities:
- Creates `/sys/fs/nfs` kset with network namespace-aware child handling.
- Creates per-net `net/nfs_client` object with writable `identifier`.
- Creates per-server kobjects, initially named `server-%d`, later renamed to superblock id and back during superblock attach/detach.
- Exposes server `shutdown`:
  - writing `1` marks `NFS_MOUNT_SHUTDOWN`,
  - shuts down main and ACL RPC clients,
  - shuts down lockd client if present,
  - shuts down the shared `nfs_client` only once all superblocks are marked shutdown.
- Optionally exposes NFSv4.1 implementation ID domain/name.
- Optionally exposes `localio` status.
- Creates sysfs links from NFS server objects to underlying SUNRPC clients.

Integration:
- Called by NFS namespace setup/teardown and server lifecycle code.
- Uses RCU for identifier storage and namespace association.
- Coordinates with lockd, RPC task cancellation, and `nfs_mark_client_ready`.

Risks and notes:
- Shutdown is global to the server/client object and intentionally cancels outstanding RPCs with `-EIO`.
- Identifier replacement uses `xchg` plus `synchronize_rcu` before freeing the old string.
