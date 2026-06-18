# File Research: sources/os/linux/linux/fs/nfs_common/nfs_ssc.c

Provides the shared registration table for NFSv4.2 server-side copy helper callbacks.

Key behavior:
- Defines and exports global `nfs_ssc_client_tbl`.
- Under `CONFIG_NFS_V4_2`, `nfs42_ssc_register()` and `nfs42_ssc_unregister()` install/remove NFSv4 client-side SSC ops.
- Under `CONFIG_NFS_V4_2`, `nfs_ssc_register()` and `nfs_ssc_unregister()` install/remove NFS filesystem-level SSC ops.
- Unregister helpers only clear pointers if the caller matches the currently registered ops.
- Without `CONFIG_NFS_V4_2`, `nfs_ssc_register()` and `nfs_ssc_unregister()` are exported no-ops.

Important interactions:
- Allows NFSD inter-server copy support to call into NFS client modules without hardwiring all callbacks directly.
- `super.c` registers the NFS client operations when NFSv4.2 support is enabled.
