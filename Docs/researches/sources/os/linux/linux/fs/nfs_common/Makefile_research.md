# File Research: sources/os/linux/linux/fs/nfs_common/Makefile

Builds Linux NFS code shared by the client and server.

Key behavior:
- Builds `nfs_acl.o` from `nfsacl.o` when `CONFIG_NFS_ACL_SUPPORT` is enabled.
- Adds include path flags for `localio_trace.o`.
- Builds `nfs_localio.o` from `nfslocalio.o` and `localio_trace.o` when `CONFIG_NFS_COMMON_LOCALIO_SUPPORT` is enabled.
- Builds `grace.o` when `CONFIG_GRACE_PERIOD` is enabled.
- Builds `nfs_ssc.o` when `CONFIG_NFS_V4_2_SSC_HELPER` is enabled.
- Builds `common.o` when `CONFIG_NFS_COMMON` is enabled.

Important interactions:
- Separates common protocol/status/ACL/localio/grace helpers from client-only `fs/nfs` and server-only `fs/nfsd`.
