# File Research: sources/os/bsd/freebsd-src/sys/fs/ext2fs/ext2_extattr.c

This file implements extended attribute list/get/set/delete/free operations for in-inode ext4 xattrs and external xattr blocks.

Key responsibilities:
- Translate Linux ext4 xattr namespaces/names to FreeBSD extattr namespaces and POSIX.1e ACL names.
- Validate attribute names and xattr entry lists.
- List and retrieve attributes from in-inode storage and external xattr blocks.
- Delete attributes, compact entries/values, and free storage when the last external attribute is removed.
- Set or replace attributes in in-inode storage or external xattr blocks.
- Clone shared external xattr blocks before modification.
- Maintain xattr entry hashes, block hashes, metadata checksums, inode `i_facl`, `i_blocks`, and inode updates.
- Free external xattr blocks during inode deletion.

Important functions:
- Namespace/name helpers: `ext2_extattr_attrnamespace_to_bsd`, `ext2_extattr_name_to_bsd`, `ext2_extattr_attrnamespace_to_linux`, `ext2_extattr_name_to_linux`, `ext2_extattr_valid_attrname`.
- Validation: `ext2_extattr_check`, `ext2_extattr_block_check`.
- Read paths: `ext2_extattr_inode_list`, `ext2_extattr_block_list`, `ext2_extattr_inode_get`, `ext2_extattr_block_get`.
- Mutation helpers: `ext2_extattr_delete_value`, `ext2_extattr_delete_entry`, `ext2_extattr_block_clone`, `ext2_extattr_set_exist_entry`, `ext2_extattr_set_new_entry`.
- Write/delete/free paths: `ext2_extattr_inode_delete`, `ext2_extattr_block_delete`, `ext2_extattr_inode_set`, `ext2_extattr_block_set`, `ext2_extattr_free`.

Important interactions:
- Uses `ext2_alloc_meta`, `ext2_blkfree`, `ext2_update`, and extattr checksum functions from `ext2_csum.c`.
- Directly reads inode table blocks for in-inode xattrs.
- External xattr blocks use `i_facl` and support shared block refcounts.

Notable risks:
- In-inode set returns `ENOSPC` if no in-inode xattr header exists; external-block set can create a new block.
- Shared xattr blocks are copy-on-write cloned before mutation.
