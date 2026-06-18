# File Research: sources/os/linux/linux-stable/fs/nfs_common/Makefile

Purpose: Build rules for NFS code shared by client and server.

Key responsibilities:
- Builds ACL support when `CONFIG_NFS_ACL_SUPPORT` is enabled.
- Builds localio support and its tracepoint object when `CONFIG_NFS_COMMON_LOCALIO_SUPPORT` is enabled.
- Builds grace period support, server-side-copy helper, and common status translation based on config symbols.
- Adds local include path for `localio_trace.o`.

Integration:
- Produces shared modules/objects consumed by NFS client and NFSD.

Risks and notes:
- Feature availability is entirely Kconfig-driven.
