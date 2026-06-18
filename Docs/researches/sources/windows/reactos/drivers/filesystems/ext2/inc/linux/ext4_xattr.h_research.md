# File Research: sources/windows/reactos/drivers/filesystems/ext2/inc/linux/ext4_xattr.h

This header defines ext4 extended attribute layout and the Ext2Fsd/lwext4-style xattr management API.

Major content:
- xattr magic, maximum refcount, and name-index constants for user, POSIX ACL, trusted, Lustre, security, system, richacl, and encryption namespaces.
- Packed on-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, `ext4_xattr_entry`.
- Alignment and navigation macros for xattr entry length, value size, next entry, name pointer, inode-body header/first entry, block header/first entry, and last-entry detection.
- `EXT4_ZERO_XATTR_VALUE` sentinel.

Runtime structures:
- `struct ext4_xattr_item`: one attribute item, including storage choice, namespace/name/data, rb-tree node, and ordered-list node.
- `struct ext4_xattr_ref`: active xattr editing context with IRP context, backing block buffer, inode MCB, raw on-disk inode, dirty flags, remaining inode/block space, VCB pointer, iterator state, rb-tree, and ordered list.

Declared APIs:
- Acquire/release xattr reference: `ext4_fs_get_xattr_ref`, `ext4_fs_put_xattr_ref`.
- Set/remove/get xattr: `ext4_fs_set_xattr`, `ext4_fs_set_xattr_ordered`, `ext4_fs_remove_xattr`, `ext4_fs_get_xattr`.
- Iterate/reset iteration, parse full names, map namespace prefixes, and purge item lists.

Role:
- Supplies extended attribute support for the Windows ext2 driver while using ext4-compatible on-disk xattr formats.

Provenance note:
- This file carries a 2015 lwext4-style permissive license header, unlike the older GPL-derived Linux headers in this group.
