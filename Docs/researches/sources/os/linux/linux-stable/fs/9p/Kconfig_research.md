# File Research: sources/os/linux/linux-stable/fs/9p/Kconfig
- Purpose: Defines kernel configuration switches for the Linux 9P filesystem client.
- Main options: `9P_FS` enables the filesystem; `9P_FSCACHE` enables FS-Cache integration; `9P_FS_POSIX_ACL` enables POSIX ACL support; `9P_FS_SECURITY` enables security xattr support.
- Integration: Ties the filesystem to the network 9P client stack and optional VFS features such as ACLs, xattrs, and caching.
- Build impact: These symbols drive object selection in `fs/9p/Makefile` and conditional code in `acl.h`, `cache.h`, and xattr/security handlers.
- Research notes: Configuration combinations are important because many 9P helper headers provide inline no-op fallbacks when optional ACL/cache support is disabled.
