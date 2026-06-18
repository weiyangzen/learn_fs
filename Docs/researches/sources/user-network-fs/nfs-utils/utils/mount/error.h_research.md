# sources/user-network-fs/nfs-utils/utils/mount/error.h

Purpose: declares common error-reporting functions for mount and umount helpers.

Important APIs: exports `nfs_strerror()`, `mount_error()`, `rpc_mount_errors()`, `sys_mount_errors()`, and `umount_error()`. It includes `parse_opt.h` because `mount_error()` accepts `struct mount_options *` for option-sensitive diagnostics.

Control flow and integration: consumed by `mount.c`, `mount_libmount.c`, `nfsmount.c`, `nfs4mount.c`, `nfsumount.c`, and network helper code to keep user-visible diagnostics consistent.

State and persistence: no state; all behavior lives in `error.c`.

Dependencies: callers must provide global `progname` as required by the implementation.

Risks and tests: signature changes affect many mount paths. Test signals are compile coverage across libmount and legacy builds, plus branch tests in `error.c` that verify callers pass the expected source, target, errno, and options values.
