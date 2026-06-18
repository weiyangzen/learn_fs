# File Research: sources/os/linux/linux/fs/ext4/xattr.h

## Purpose
Defines ext4 xattr on-disk formats, constants, layout macros, helper structs, lock helpers, and exported xattr APIs.

## Key Definitions
- Magic and limits: `EXT4_XATTR_MAGIC`, `EXT4_XATTR_REFCOUNT_MAX`, `EXT4_XATTR_SIZE_MAX`.
- Namespace indexes: user, POSIX ACL access/default, trusted, Lustre, security, system, richacl, encryption, and Hurd.
- On-disk structures: `ext4_xattr_header`, `ext4_xattr_ibody_header`, and `ext4_xattr_entry`.
- Layout macros: `EXT4_XATTR_LEN`, `EXT4_XATTR_NEXT`, `EXT4_XATTR_SIZE`, `IHDR`, `ITAIL`, `IFIRST`, `BHDR`, `BFIRST`, `IS_LAST_ENTRY`.
- `EXT4_INODE_HAS_XATTR_SPACE()` verifies that an inode has enough extra inode area to host an in-inode xattr header and padding.

## API Surface
Declares get/list/set paths, journal-credit helpers, inode deletion cleanup, extra-isize expansion, EA inode eviction, ibody find/set/get helpers, mbcache create/destroy, inode usage accounting, and xattr handler arrays.

## Notable Design Detail
The inline xattr write lock helpers save and restore `EXT4_STATE_NO_EXPAND`. That state is intentionally overloaded to mean both “do not try further inline expansion” and “xattr write lock is held, avoid recursive expansion.”
