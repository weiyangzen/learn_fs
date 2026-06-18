# File Research: sources/os/linux/linux/fs/ecryptfs/ecryptfs_kernel.h

## Purpose
Central private header for the eCryptfs kernel module. It defines constants, private structures, inline accessors, operation exports, cache globals, and cross-file function declarations.

## Main Responsibilities
- Defines file-format constants, default sizes, packet tags, metadata marker, filename prefixes, and versioning mask.
- Defines per-file, per-inode, per-file-handle, per-superblock, mount-wide, message, daemon, key, and filename state structures.
- Provides inline helpers for lower object access: file, inode, dentry, path, superblock.
- Declares VFS operation tables, address-space operations, xattr handlers, caches, module parameters, crypto helpers, keystore helpers, messaging helpers, and lower I/O helpers.

## Important Structures
- `struct ecryptfs_crypt_stat`: per-inode crypt state, including flags, file version, extent/header sizes, cipher name, FEK, root IV, key signatures, skcipher context, and mutexes.
- `struct ecryptfs_inode_info`: upper inode wrapper, lower inode pointer, shared lower file, lower file refcount, and `crypt_stat`.
- `struct ecryptfs_mount_crypt_stat`: mount policy, global auth token list, default ciphers/key sizes, filename encryption key signature, and feature flags.
- `struct ecryptfs_global_auth_tok`: mount-wide reference to keyring auth tokens.
- `struct ecryptfs_key_tfm`: cached crypto transform plus mutex and cipher name.
- `struct ecryptfs_msg_ctx` and `struct ecryptfs_daemon`: messaging state for userspace daemon request/response handling.
- `struct ecryptfs_file_info` and `struct ecryptfs_sb_info`: upper file and superblock private state.

## Key Flags
Per-file flags include initialized, policy applied, encrypted, key valid, xattr metadata, encrypted view, filename encryption, FNEK/FEK filename key mode, unlink signatures, and initialized size.

Mount flags include plaintext passthrough, xattr metadata, encrypted view, initialized mount state, global filename encryption, mount FNEK mode, FEK mode, and mount-auth-token-only enforcement.

## Inline Accessors
The header establishes the stacking contract:
- Upper file `private_data` points to `ecryptfs_file_info`, which stores the lower file.
- Upper inode embeds `ecryptfs_inode_info`, which stores the lower inode and crypt state.
- Upper dentry `d_fsdata` stores the lower dentry.
- Upper superblock `s_fs_info` stores lower superblock, lower mount, and mount crypt policy.

## Conditional Messaging
If `CONFIG_ECRYPT_FS_MESSAGING` is disabled, messaging functions become no-op/error inline stubs. This lets keystore code compile while returning `-ENOTCONN`/`-ENOMSG` for userspace daemon operations.

## Dependencies
- Linux crypto, keyring, VFS, fsstack, scatterlist, hash, namespace, backing-dev, and public `linux/ecryptfs.h`.
- All eCryptfs implementation files include this header.

## Risks and Notes
- This header couples most module internals; structure changes affect crypto, inode, file, main, messaging, and keystore code simultaneously.
- Several constants reflect legacy eCryptfs wire formats and must stay compatible with existing encrypted files.
