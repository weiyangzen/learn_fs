# File Research: sources/os/linux/linux/fs/nfs/Kconfig

Defines Linux NFS client configuration options.

Major options:
- `NFS_FS`: base NFS client support; depends on networking, file locking, and multiuser support; selects CRC32, LOCKD, SUNRPC, and NFS common code.
- `NFS_V2`, `NFS_V3`, `NFS_V3_ACL`.
- `NFS_V4`, `NFS_V4_0`, `NFS_V4_2`.
- `NFS_SWAP`.
- `PNFS_FILE_LAYOUT`, `PNFS_BLOCK`, `PNFS_FLEXFILE_LAYOUT`.
- `ROOT_NFS`.
- `NFS_FSCACHE`.
- DNS resolver options.
- Debug and UDP-disable options.
- `NFS_V4_2_READ_PLUS`.

Important relationships:
- `NFS_FSCACHE` depends on `NFS_FS` and selects `NETFS_SUPPORT` plus `FSCACHE`.
- `PNFS_BLOCK` depends on `NFS_V4 && BLK_DEV_DM` and defaults to `NFS_V4`.
- NFSv4 selects key management and SUNRPC backchannel support.
- Kernel DNS resolver is selected unless legacy DNS resolver is enabled.

Role in this group:
- Connects NFS client caching to the generic netfs/FS-Cache stack researched above.
- Enables block pNFS layout driver support researched in `blocklayout.c`.
