# File Research: sources/os/linux/linux-stable/fs/ecryptfs/main.c

## Summary
Implements eCryptfs module setup, mount parsing/validation, filesystem registration, superblock creation/destruction, lower-file reference management, sysfs version reporting, and kmem-cache lifecycle.

## Main Responsibilities
- Define module parameters for verbosity, message buffer length, message wait timeout, and estimated user count.
- Open and refcount shared lower files for upper regular inodes.
- Parse fs_context mount parameters for signatures, ciphers, key sizes, passthrough, xattr metadata, encrypted view, filename encryption, and auth-token policy.
- Validate required mount options, cipher support, cached transforms, and registered auth tokens.
- Reject unsupported mount situations: missing source, recursive eCryptfs mount, idmapped lower mount, failed owner check, excessive stack depth, and FIPS mode.
- Build the eCryptfs superblock over a lower directory and mirror lower superblock limits/flags.
- Initialize and destroy module kmem caches.
- Register `/sys/fs/ecryptfs/version`.
- Initialize and tear down kthread, messaging, crypto, and filesystem registration.

## Key APIs
- `ecryptfs_get_lower_file()`
- `ecryptfs_put_lower_file()`
- `ecryptfs_parse_param()`
- `ecryptfs_validate_options()`
- `ecryptfs_get_tree()`
- `ecryptfs_init()` / `ecryptfs_exit()`

## Important Behavior
A regular upper inode keeps at most one lower file open. The first caller opens it through `ecryptfs_init_lower_file()`, increments are counted atomically, and the final put writes back the upper mapping before `fput()`.

Mount validation requires at least one auth-token signature and verifies cipher support by creating or finding cached transforms. Filename encryption defaults to the content cipher and key size unless filename-specific options are supplied.

Encrypted-view mounts force xattr metadata and make the eCryptfs mount read-only. Lower read-only mounts also force the upper mount read-only.

## Research Notes
This file is the module lifecycle and mount-policy entry point. It coordinates most other files: caches for all private objects, kthread lower opens, messaging for ecryptfsd, crypto transform cache initialization, and VFS registration.
