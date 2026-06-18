# File Research: sources/os/linux/linux-stable/fs/ext4/symlink.c

## Purpose

`symlink.c` implements ext4 symlink inode operations. Most symlink behavior is handled by generic VFS code; this file supplies ext4-specific link target retrieval for fast symlinks, block-backed symlinks, inline-data leftovers, and encrypted symlinks.

## Main Flows

- `ext4_encrypted_get_link()` returns decrypted symlink targets through `fscrypt_get_symlink()`.
  - For fast symlinks, it reads ciphertext from `EXT4_I(inode)->i_data`.
  - For non-fast symlinks, it reads logical block 0 with `ext4_bread()`.
  - A missing block is reported as ext4 corruption via `EXT4_ERROR_INODE()` and `-EFSCORRUPTED`.
  - It releases the temporary buffer head before returning the fscrypt-managed result.
- `ext4_encrypted_symlink_getattr()` delegates base attributes to `ext4_getattr()` and then adjusts encrypted symlink size through `fscrypt_symlink_getattr()`.
- `ext4_get_link()` handles normal unencrypted symlink targets.
  - If inline data is present, new inline symlink creation is not supported, but old inline symlink data can still be read through `ext4_read_inline_link()`.
  - For RCU pathwalk (`dentry == NULL`), it only returns a cached uptodate block; otherwise it returns `-ECHILD` so lookup can retry in ref-walk mode.
  - For normal lookup, it reads block 0 with `ext4_bread()`, validates it exists, sets delayed cleanup with `ext4_free_link()`, terminates the target with `nd_terminate_link()`, and returns `bh->b_data`.
- `ext4_free_link()` releases buffer heads used as delayed link storage.

## Exported Operation Tables

- `ext4_encrypted_symlink_inode_operations`
  - `.get_link = ext4_encrypted_get_link`
  - `.setattr = ext4_setattr`
  - `.getattr = ext4_encrypted_symlink_getattr`
  - `.listxattr = ext4_listxattr`
- `ext4_symlink_inode_operations`
  - normal block-backed or inline symlink handling through `ext4_get_link()`.
- `ext4_fast_symlink_inode_operations`
  - fast in-inode unencrypted symlinks use `simple_get_link()`.

## Integration Points

This file depends on:

- `ext4_inode_is_fast_symlink()` from inode logic.
- `ext4_bread()` and `ext4_getblk()` for block-backed symlink storage.
- Inline data helpers for legacy inline symlink targets.
- fscrypt for encrypted symlink decoding and encrypted symlink getattr.
- xattr handlers through the inode operation tables.

## Edge Cases

- RCU lookup never performs blocking disk I/O; it returns `-ECHILD` unless the needed block is already cached and uptodate.
- Missing symlink blocks are treated as filesystem corruption.
- Inline symlink creation is intentionally not supported here; only reading existing inline data remains.
- Buffer lifetime is managed with delayed calls so returned link pointers remain valid through VFS path resolution.
