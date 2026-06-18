# File Research: sources/os/bsd/netbsd-src/sys/ufs/ext2fs/ext2fs_xattr.h

This header defines ext2 extended attribute constants, on-disk structures, alignment macros, prefix indexes, and ext2fs xattr VOP prototypes.

Key contents:
- Include guard `_UFS_EXT2FS_EXT2FS_XATTR_H_`.
- Kernel-only definitions for ext2fs xattrs.
- `EXT2FS_XATTR_MAGIC`: `0xEA020000`.
- `EXT2FS_XATTR_NAME_LEN_MAX`: 255.
- `EXT2FS_XATTR_REFCOUNT_MAX`: 1024.
- `struct ext2fs_xattr_ibody_header`: Inline inode xattr header with magic.
- `struct ext2fs_xattr_header`: External xattr block header with magic, refcount, blocks, hash, checksum, and reserved words.
- `struct ext2fs_xattr_entry`: On-disk xattr entry containing name length/index, value offset/block/size, hash, and flexible name bytes.
- `EXT2FS_XATTR_IS_LAST_ENTRY`: Treats zero word as terminator and also stops if the next entry would exceed the provided end pointer.
- `EXT2FS_XATTR_LEN` and `EXT2FS_XATTR_NEXT`: 4-byte aligned entry sizing and iteration.
- `EXT2FS_XATTR_IFIRST` and `EXT2FS_XATTR_BFIRST`: Locate first entry after inline/block header.
- Prefix index constants for none, user, POSIX ACL access/default, trusted, security, system, richacl, and encryption.
- Prototypes for `ext2fs_getextattr`, `ext2fs_setextattr`, `ext2fs_listextattr`, and `ext2fs_deleteextattr`.

Important interactions:
- Consumed directly by `ext2fs_xattr.c`.
- VOP xattr functions are registered in `ext2fs_vnops.c`.

Notable behavior:
- The macros assume xattr entries are 4-byte aligned.
- `e_value_block` is documented as unsupported and expected to be zero.
