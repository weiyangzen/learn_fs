# sources/user-network-fs/nfs-utils/utils/mount/nfs_mount.h

Purpose: defines legacy NFSv2/v3 userspace-to-kernel mount data structures and mount frontend prototypes.

Important APIs and types: constants include `NFS_MOUNT_VERSION` and `NFS_MAX_CONTEXT_LEN`. File handle structs `nfs2_fh` and `nfs3_fh` are used within the mount data ABI. The header declares `nfsmount()` and `nfsumount()`.

Control flow and integration: `nfsmount.c` fills the ABI structure based on MOUNT protocol results and option parsing; `mount.c` and `mount_libmount.c` call `nfsmount()` for legacy NFS mounts and dispatch to `nfsumount()` in non-libmount umount mode.

State and persistence: no state; structure layout/defines are compatibility contracts with older kernel mount interfaces.

Dependencies: includes IPv4 networking headers because mount data contains addresses.

Risks and tests: ABI changes are risky across kernel versions. Test signals include builds against old headers, selecting correct mount data version through `discover_nfs_mount_data_version()`, and NFSv2/v3 file handle copy behavior.
