# File Research: sources/os/bsd/netbsd-src/sys/ufs/ufs/acl.h

This header declares UFS ACL support.

Key contents:
- Declares internal NFSv4 ACL get/set helpers.
- Declares POSIX.1e ACL set helper.
- Declares ACL/mode synchronization helpers between inode mode bits and ACL entries.
- Under `UFS_ACL`, maps vnode ACL operations to real functions.
- Without `UFS_ACL`, maps ACL operations to `genfs_eopnotsupp`.

Role:
- Compile-time switch and function surface for UFS POSIX.1e and NFSv4 ACL integration.
