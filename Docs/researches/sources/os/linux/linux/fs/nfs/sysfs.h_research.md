# File Research: sources/os/linux/linux/fs/nfs/sysfs.h

Declares the NFS client sysfs data structures and helper interface.

Key behavior:
- Defines `CONTAINER_ID_MAXLEN` as 64 bytes.
- Defines `struct nfs_netns_client`, containing:
  - A client kobject.
  - A containing `net` kobject.
  - The owning `struct net`.
  - An RCU-protected namespace/container identifier string.
- Declares global `nfs_net_kobj`.
- Declares sysfs init/exit, per-netns setup/destroy, RPC-client link creation, server add, server/superblock rename transitions, and server removal helpers.

Important interactions:
- Included by `super.c` and `sysfs.c`.
- Forms the small public contract between NFS net namespace management, server lifecycle, and sysfs exposure.
