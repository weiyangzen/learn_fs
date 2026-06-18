# File Research: sources/os/linux/linux-stable/fs/nfs/sysfs.h

Purpose: Declares NFS sysfs data structures and lifecycle helpers.

Key responsibilities:
- Defines `CONTAINER_ID_MAXLEN`.
- Defines `struct nfs_netns_client` containing two kobjects, a net pointer, and RCU-protected identifier.
- Declares sysfs init/exit, per-net setup/destroy, RPC-client link creation, server add/move/remove helpers.

Integration:
- Included by NFS client namespace and superblock/server code.
- Paired with implementation in `sysfs.c`.

Risks and notes:
- Header exposes only lifecycle and linking APIs, keeping sysfs details mostly private to `sysfs.c`.
