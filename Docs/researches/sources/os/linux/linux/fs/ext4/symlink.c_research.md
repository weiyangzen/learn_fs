# File Research: sources/os/linux/linux/fs/ext4/symlink.c

## Purpose
Provides ext4 symlink inode operations, including fast symlinks, block-backed symlinks, inline-data symlink remnants, and encrypted symlink decoding.

## Main Elements
- `ext4_encrypted_get_link()`: fetches symlink bytes from fast symlink inode data or block 0, then delegates decoding to `fscrypt_get_symlink()`.
- `ext4_encrypted_symlink_getattr()`: combines normal ext4 getattr with fscrypt symlink size adjustment.
- `ext4_get_link()`: reads normal symlink targets from inline data or block 0, supports RCU-walk fallback with `-ECHILD`, terminates the link buffer, and arranges delayed buffer release.
- `ext4_free_link()`: delayed-call buffer release helper.
- Inode operation tables: `ext4_encrypted_symlink_inode_operations`, `ext4_symlink_inode_operations`, and `ext4_fast_symlink_inode_operations`.

## Dependencies And Integration
Uses VFS namei delayed-call link handling, buffer heads through `ext4_bread()`/`ext4_getblk()`, ext4 inline-data helpers, and fscrypt symlink helpers. The operation tables are selected when ext4 instantiates symlink inodes.

## Behavioral Notes
Fast unencrypted symlinks use `simple_get_link()` because their target is stored directly in inode data. Encrypted symlinks must decode ciphertext from either inline inode data or an external block. Non-encrypted block symlinks use cached-nowait lookup during RCU-walk and force pathwalk retry when the buffer is unavailable or not uptodate.

## Risk Notes
Correctness depends on rejecting bad symlink block mappings and returning `-EFSCORRUPTED` for missing block-backed symlink data. The inline-data path is read-only compatibility support: new inline symlinks are not created here, but old leftovers can still be read.
