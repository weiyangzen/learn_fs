# File Research: sources/os/linux/linux-stable/fs/nfs/Kconfig

Defines Linux NFS client configuration options.

Key options:
- `NFS_FS` enables core NFS client support and selects CRC32, LOCKD, SUNRPC, NFS_COMMON, and conditional ACL support.
- Version options cover NFSv2, NFSv3, NFSv3 ACLs, NFSv4, NFSv4.0, and NFSv4.2.
- pNFS layout modules include file, block, and flexfile layouts; `PNFS_BLOCK` depends on `NFS_V4 && BLK_DEV_DM`.
- `NFS_FSCACHE` selects `NETFS_SUPPORT` and `FSCACHE`, connecting NFS to the netfs/FS-Cache files in this group.
- Other options include swap over NFS, root over NFS, DNS resolver choice, debug, UDP disable default, migration, security labels, and READ_PLUS.

Research relevance:
- This file controls whether netfs caching and pNFS block layout code in this group is built.
