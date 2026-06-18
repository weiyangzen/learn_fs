# File Research: sources/os/linux/linux-stable/fs/ext4/xattr.h

## Purpose
Defines ext4 on-disk extended attribute structures, constants, layout macros, namespace indexes, search helper structs, lock helpers, and exported xattr APIs.

## Main Components
- On-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, and `ext4_xattr_entry`.
- Namespace indexes include user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd.
- Layout macros compute padded entry/value sizes and locate first/next entries in ibody or block storage.
- `EXT4_XATTR_SIZE_MAX` is a consistency-check ceiling larger than current `XATTR_SIZE_MAX` to avoid overflow-sensitive checks.
- `EXT4_XATTR_MIN_LARGE_EA_SIZE()` defines when external EA inode storage becomes worthwhile.
- Search and mutation carrier structs include `ext4_xattr_info`, `ext4_xattr_search`, `ext4_xattr_ibody_find`, and `ext4_xattr_inode_array`.
- Write lock helpers wrap `xattr_sem` and temporarily set `EXT4_STATE_NO_EXPAND` to avoid recursive inode expansion.

## Exported Interfaces
Declares get/set/list operations, credit estimation, ibody find/get/set helpers, inode delete/free routines, EA inode eviction, cache creation/destruction, security initialization, lockdep class setup, and inode usage accounting.

## Research Notes
This header is the contract for ext4 xattr layout. Any format or macro change has direct disk-format implications.
