# File Research: sources/os/linux/linux-stable/fs/9p/vfs_inode_dotl.c
- Purpose: Implements Linux 9P2000.L inode operations with dotl-specific protocol calls and metadata formats.
- Main functions: `v9fs_inode_from_fid_dotl`, `v9fs_open_to_dotl_flags`, `v9fs_vfs_create_dotl`, `v9fs_vfs_atomic_open_dotl`, `v9fs_vfs_getattr_dotl`, `v9fs_vfs_setattr_dotl`, `v9fs_stat2inode_dotl`, symlink/link/mknod/get_link/refresh helpers.
- Dotl protocol: Uses `p9_client_getattr_dotl`, `p9_client_setattr`, `p9_client_create_dotl`, `p9_client_mkdir_dotl`, `p9_client_symlink`, `p9_client_link`, `p9_client_mknod_dotl`, and `p9_client_readlink`.
- Attribute mapping: Converts Linux open flags and iattr valid bits to dotl flags/masks; maps `p9_stat_dotl` into inode fields.
- ACL integration: Creation helpers prepare inherited POSIX ACLs and write them after successful remote object creation.
- Operation tables: Exports dotl directory, file, and symlink inode operations.
- Risks: Dotl mode/flag mapping must match server expectations; ACL and gid inheritance during create affect POSIX compatibility.
