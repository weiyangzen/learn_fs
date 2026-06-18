# File Research: sources/os/linux/linux/fs/9p/Kconfig

## Summary
Defines kernel configuration options for the 9p filesystem client.

## Main Contents
- `9P_FS`: tristate Plan 9 Resource Sharing filesystem, depending on `NET_9P` and selecting `NETFS_SUPPORT`.
- `9P_FSCACHE`: optional FS-Cache support for 9p clients.
- `9P_FS_POSIX_ACL`: optional POSIX ACL support, selecting `FS_POSIX_ACL`.
- `9P_FS_SECURITY`: optional security-label xattr support for LSMs such as SELinux.

## Important Details
`9P_FSCACHE` has dependency logic covering both module and built-in combinations with `FSCACHE`. POSIX ACL is nested under `if 9P_FS`; security labels depend directly on `9P_FS`.

## Risks
Feature availability is compile-time gated. ACL and security xattr behavior in source files depends on these symbols being selected.
