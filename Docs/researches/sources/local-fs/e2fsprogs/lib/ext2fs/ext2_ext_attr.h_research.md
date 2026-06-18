# File Research: sources/local-fs/e2fsprogs/lib/ext2fs/ext2_ext_attr.h

## Purpose
Defines the ext2/ext4 on-disk extended attribute block format and helper macros used by both userspace e2fsprogs and optional kernel-facing code.

## Key Definitions
- `EXT2_EXT_ATTR_MAGIC_v1`, `EXT2_EXT_ATTR_MAGIC`: valid EA block magic values.
- `EXT2_EXT_ATTR_REFCOUNT_MAX`: maximum shared EA block refcount.
- `struct ext2_ext_attr_header`: EA block header with magic, refcount, block count, aggregate hash, checksum, and reserved fields.
- `struct ext2_ext_attr_entry`: EA entry with name length/index, value offset, optional external EA inode, value size, entry hash, and inline trailing name bytes.
- Alignment macros:
  - `EXT2_EXT_ATTR_LEN`
  - `EXT2_EXT_ATTR_NEXT`
  - `EXT2_EXT_ATTR_SIZE`
  - `EXT2_EXT_IS_LAST_ENTRY`
  - `EXT2_EXT_ATTR_NAME`
- `EXT2_XATTR_SIZE_MAX`: consistency-check cap of `1 << 24`.

## Integration
Included by `ext2fs.h` and implemented heavily by `ext_attr.c`. Its structures are directly serialized to and from disk, so layout and alignment are format-critical.

## Risks and Notes
- The entry list is packed and terminated by a zero word; malformed name length, value offset, or value size can cause parser boundary failures.
- `e_value_inum` supports the ext4 `ea_inode` feature, where large values live in a separate inode.
- Checksums are tied to UUID, inode/block identity, and EA contents.
