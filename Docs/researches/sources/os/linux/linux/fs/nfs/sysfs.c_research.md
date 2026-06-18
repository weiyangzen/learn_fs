# File Research: sources/os/linux/linux/fs/nfs/sysfs.c

Implements the NFS client sysfs hierarchy for per-network-namespace client state and per-server control/status files.

Key behavior:
- Creates the top-level `/sys/fs/nfs` kset with network-namespace child support.
- For each NFS network namespace, creates `net/nfs_client` kobjects and exposes a writable `identifier` attribute capped by `CONTAINER_ID_MAXLEN`.
- Stores the namespace identifier through an RCU-protected string pointer and safely frees old values after `synchronize_rcu()`.
- Provides setup/destroy functions for per-netns sysfs objects.
- Implements server shutdown control:
  - `shutdown` reads whether `NFS_MOUNT_SHUTDOWN` is set.
  - Writing `1` marks the mount shutdown, cancels main/ACL RPC clients, shuts down lockd state if present, and shuts down the shared `nfs_client` only after all superblocks are shutdown.
- Optionally exposes NFSv4.1 implementation ID domain/name attributes.
- `nfs_sysfs_link_rpc_client()` creates links from an NFS server kobject to RPC client sysfs kobjects.
- Adds per-server kobjects named `server-<id>`, with namespace-aware attributes.
- Optionally exposes `localio` when `CONFIG_NFS_LOCALIO` is enabled.
- Renames server kobjects to the superblock ID when attached to a superblock and back to `server-<id>` when detached.
- `nfs_sysfs_remove_server()` unlinks the server kobject from sysfs.

Important interactions:
- Used by `super.c` during superblock fill and teardown.
- Uses lockd shutdown hooks and RPC task cancellation to make sysfs shutdown operational, not merely informational.
- Coordinates namespace isolation through `net_ns_type_operations` and kobject namespace callbacks.
