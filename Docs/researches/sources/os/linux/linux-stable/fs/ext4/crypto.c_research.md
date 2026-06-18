# File Research: sources/os/linux/linux-stable/fs/ext4/crypto.c

## Purpose

Integrates ext4 with Linux fscrypt for encrypted filenames, encryption policy context storage, password salt ioctl support, and fscrypt operation registration.

## Main Responsibilities

- Converts `fscrypt_name` into ext4’s `ext4_filename`.
- Prepares encrypted/casefold-aware filenames for create and lookup.
- Frees filename crypto and casefold buffers.
- Implements `EXT4_IOC_GET_ENCRYPTION_PWSALT` behavior.
- Gets and sets encryption context xattrs.
- Registers ext4 fscrypt operations.

## Key Operations

- `ext4_fname_setup_filename()` calls `fscrypt_setup_filename()`, maps fields into `ext4_filename`, and sets up case-insensitive filename state.
- `ext4_fname_prepare_lookup()` calls `fscrypt_prepare_lookup()` for dentries and then prepares ext4 casefold state.
- `ext4_fname_free_filename()` releases fscrypt and ext4 casefold filename buffers.
- `ext4_ioctl_get_encryption_pwsalt()` lazily generates `s_encrypt_pw_salt` in the superblock under a journal transaction, updates checksum, dirties metadata, and copies the 16-byte salt to userspace.
- `ext4_get_context()` reads the encryption context xattr.
- `ext4_set_context()` stores encryption context xattrs, refuses root inode encryption, rejects DAX conflicts, converts inline data, handles new-inode inherited context with caller-supplied handle, and otherwise starts its own journal transaction with ENOSPC retry support.
- `ext4_get_dummy_policy()` exposes the dummy encryption policy from `sbi`.
- `ext4_has_stable_inodes()` reports the stable inode feature to fscrypt.

## fscrypt Operations

`ext4_cryptops` sets:

- inode crypto info offset.
- bounce-page requirement.
- 32-bit inode support.
- subblock data unit support.
- legacy key prefix `ext4:`.
- context get/set callbacks.
- dummy policy callback.
- empty-directory callback.
- stable-inode callback.

## Dependencies

- Includes quotaops, uuid helpers, `ext4.h`, `xattr.h`, and `ext4_jbd2.h`.
- Uses fscrypt, ext4 xattrs, journaling, inline-data conversion, inode flag updates, and superblock checksums.

## Research Notes

Encryption state is persisted as an xattr and journaled metadata. The file deliberately blocks encryption of the root inode and DAX-encrypted conflicts. Filename preparation also composes fscrypt with ext4 casefold support.
