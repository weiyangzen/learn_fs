# File Research: sources/os/linux/linux/fs/ext4/Kconfig

## Purpose
Defines kernel configuration options for building ext4 and optional ext4 features.

## Main Responsibilities
- `EXT4_FS` selects required infrastructure: buffer heads, JBD2, CRC helpers, iomap, and encryption algorithms when fs encryption is enabled.
- `EXT4_USE_FOR_EXT2` allows ext4 to mount ext2 filesystems when ext2 is not built.
- `EXT4_FS_POSIX_ACL` enables POSIX ACL support and selects `FS_POSIX_ACL`.
- `EXT4_FS_SECURITY` enables security label xattr support.
- `EXT4_DEBUG` enables runtime debug messages.
- `EXT4_KUNIT_TESTS` builds ext4 KUnit tests.

## Integration Points
Controls which objects are compiled by the ext4 Makefile and which VFS/security/fscrypt features are available.

## Risks and Edge Cases
`EXT4_USE_FOR_EXT2` changes which driver services ext2 mounts. Optional ACL/security/encryption support affects on-disk feature usability and mount/runtime behavior.
