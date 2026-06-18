# File Research: sources/os/linux/linux/fs/jfs/symlink.c

JFS symlink inode operation tables.

Key responsibilities:
- Defines `jfs_fast_symlink_inode_operations` for inline symlink targets using `simple_get_link`.
- Defines `jfs_symlink_inode_operations` for page-cache-backed symlink targets using `page_get_link`.
- Shares JFS setattr and listxattr support across both symlink forms.

Important interactions:
- Selected by `jfs_symlink()` in `namei.c` depending on whether the symlink target fits in the inode inline data area.
- Uses `jfs_setattr()` and `jfs_listxattr()` from JFS inode/xattr subsystems.

Invariants and risks:
- Correct operation table selection depends on the inline target size threshold used during symlink creation.
- Long symlinks rely on normal page-cache address-space operations configured by the creator.
