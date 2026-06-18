# File Research: sources/os/linux/linux/fs/ext4/crypto.c

## Purpose
Implements ext4 integration with fscrypt filename handling, encryption policy/context storage, password salt ioctl, and fscrypt operation registration.

## Main Responsibilities
- Converts `fscrypt_name` into `ext4_filename` through `ext4_fname_from_fscrypt_name()`.
- `ext4_fname_setup_filename()` and `ext4_fname_prepare_lookup()` prepare encrypted and casefold-aware names for create/lookup paths.
- `ext4_fname_free_filename()` releases fscrypt and casefold buffers.
- `ext4_ioctl_get_encryption_pwsalt()` returns or lazily generates the filesystem encryption password salt in the superblock under a journal transaction.
- `ext4_get_context()` reads encryption context xattrs.
- `ext4_set_context()` writes encryption context xattrs, handles new-inode versus existing-inode transaction modes, rejects root-directory encryption, rejects DAX conflicts, converts inline data, sets inode encryption flags, and retries ENOSPC where appropriate.
- Registers `ext4_cryptops` for fscrypt.

## Integration Points
Uses fscrypt, ext4 xattrs, JBD2, quota initialization, inline-data conversion, inode flag synchronization, superblock checksums, random UUID generation, and mount write access.

## Risks and Edge Cases
Root directory encryption is forbidden because `lost+found` expectations would break. Existing nonempty DAX inodes and DAX-flagged inodes cannot receive encryption context. Salt generation mutates the superblock and must update checksum and journal metadata.
