# File Research: sources/os/linux/linux-stable/fs/ecryptfs/ecryptfs_kernel.h

## Summary
Shared internal header for eCryptfs. It defines constants, metadata packet tags, core private structures, inline accessors linking upper and lower objects, optional messaging stubs, cache externs, operation-table externs, and internal function prototypes.

## Main Responsibilities
- Define default extent, IV, message, xattr, cipher, key, marker, filename, and packet-size constants.
- Define eCryptfs packet tags for RFC2440-inspired key packets and filename-encryption packets.
- Define cryptographic state structures including `ecryptfs_crypt_stat`, `ecryptfs_mount_crypt_stat`, `ecryptfs_key_sig`, `ecryptfs_key_tfm`, and `ecryptfs_global_auth_tok`.
- Define filesystem private state: `ecryptfs_inode_info`, `ecryptfs_sb_info`, and `ecryptfs_file_info`.
- Define messaging structures for ecryptfsd integration: `ecryptfs_message`, `ecryptfs_msg_ctx`, and `ecryptfs_daemon`.
- Provide inline helpers for lower inode, dentry, superblock, path, and file mappings.
- Provide key-payload helpers for user keys and optional encrypted-key support.
- Declare eCryptfs operation tables, kmem caches, module parameters, and internal APIs.

## Key Data Structures
- `struct ecryptfs_crypt_stat`: per-inode encryption flags, file version, sizes, cipher, FEK, root IV, transform, and key signature list.
- `struct ecryptfs_mount_crypt_stat`: mount-wide auth token list, cipher defaults, FNEK settings, and mount policy flags.
- `struct ecryptfs_inode_info`: VFS inode wrapper plus lower inode, lower-file refcounting state, and crypt state.
- `struct ecryptfs_daemon` and `struct ecryptfs_msg_ctx`: userspace-daemon routing and pending response tracking.

## Important Behavior
The header centralizes flags that control major behavior: plaintext passthrough, xattr metadata, encrypted view, filename encryption, mount-auth-token-only, encrypted file state, metadata location, key validity, and initialized `i_size`.

When `CONFIG_ECRYPT_FS_MESSAGING` is disabled, messaging functions are compiled as stubs returning connection/message errors. This lets most eCryptfs code build while public-key packet operations fail cleanly without daemon support.

## Research Notes
This file is the dependency hub for the eCryptfs module. The most important invariants are upper-to-lower object ownership, metadata-size calculation through `ecryptfs_lower_header_size()`, auth-token lifetime, and matching the packet constants used by `crypto.c` and `keystore.c`.
