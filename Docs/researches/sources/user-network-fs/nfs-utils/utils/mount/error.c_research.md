# sources/user-network-fs/nfs-utils/utils/mount/error.c

Purpose: centralizes NFS mount/umount error presentation and maps NFS protocol status values to local errno text.

Important APIs: `rpc_mount_errors()`, `sys_mount_errors()`, `mount_error()`, `umount_error()`, and `nfs_strerror()`. Internal `rpc_strerror()` formats `rpc_createerr`.

Control flow: foreground errors go to stderr through `nfs_error`/`fprintf`; background mount errors go to syslog. `mount_error()` switches on errno and provides more specific messages for access denied, bad options, unsupported protocol, busy mountpoints, RPC mount failures, and RDMA routing hints. `nfs_strerror()` scans `nfs_errtbl` for NFSv2/v3 status mappings.

State and persistence: a static `errbuf` is reused for formatted messages; syslog is opened once per background path. No durable state is written.

Dependencies and integration: depends on libtirpc `rpc_createerr`, nls gettext wrappers, mount option parser tables, and NFS protocol status constants.

Risks: static buffer is not thread-safe, though helpers are single-process/single-thread. Some foreground `sys_mount_errors()` non-timeout paths intentionally do not append detailed text. Test signals include each errno branch, RPC timeout retry/give-up variants, background syslog path, unknown NFS status, and RDMA-specific `EPROTO`.
