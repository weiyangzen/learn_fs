# File Research: sources/os/bsd/dragonflybsd/sys/vfs/ufs/dinode.h

UFS on-disk inode layout and mode constant header.

Key responsibilities:
- Defines special inode numbers: root inode `UFS_ROOTINO` as 2 and whiteout placeholder `UFS_WINO` as 1.
- Defines direct and indirect block pointer counts: `UFS_NDADDR` and `UFS_NIADDR`.
- Defines packed-by-field `struct ufs1_dinode`, the UFS1 on-disk inode containing mode, link count, legacy ids/inumber union, size, timestamps, direct/indirect block arrays, flags, block count, generation, uid/gid, and DragonFly 2019 high timestamp extension fields.
- Defines compatibility aliases for old uid/gid, LFS inode number, device number overlay, and short symlink overlay.
- Defines `UFS1_MAXSYMLINKLEN` as the storage available in direct/indirect block pointer space.
- Defines file permission bits and UFS file type bits.

Dependencies:
- Includes `ufs_types.h` for UFS integer and disk-address types.
- Consumed by inode load/update code and UFS/FFS metadata manipulation.

Notable risks:
- This is on-disk ABI; field layout and sizes must not change without filesystem-format migration.
- The direct block array is overloaded for devices and short symlinks, so consumers must respect inode type before interpretation.
- DragonFly's 48-bit timestamp extensions reuse former spare fields, which affects cross-system compatibility.
