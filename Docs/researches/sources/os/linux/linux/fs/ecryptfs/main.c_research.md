# File Research: sources/os/linux/linux/fs/ecryptfs/main.c

## Purpose
Implements eCryptfs module setup/teardown, filesystem registration, fs_context mount parsing and validation, superblock construction, shared lower-file lifetime management, kmem caches, and sysfs version exposure.

## Main Responsibilities
- Define module parameters for verbosity, messaging buffer count, daemon response timeout, and estimated user count.
- Manage per-inode shared lower-file open/close reference counting.
- Parse and validate eCryptfs mount options.
- Build the stacked superblock on top of a lower directory.
- Create and destroy all slab caches used by the module.
- Initialize and tear down sysfs, kthread, messaging, crypto, and filesystem registration.

## Mount Options
Supported parameters include key signatures, cipher name, key bytes, plaintext passthrough, xattr metadata, encrypted view, FNEK signature, filename cipher, filename key bytes, unlink signatures, mount-auth-token-only mode, and lower-root UID check.

`ecryptfs_validate_options()` requires at least one signature, supplies default ciphers/key sizes, validates cipher codes, initializes cached cipher transforms, initializes filename cipher transforms if needed, and resolves mount-global auth tokens.

## Superblock Setup
`ecryptfs_get_tree()` validates source path and mount options, rejects FIPS mode, creates an anonymous superblock, resolves the lower directory, rejects recursive eCryptfs mounts and idmapped mounts, optionally checks lower root ownership, copies lower POSIX ACL and time/block limits, enforces read-only when lower is read-only or encrypted-view is requested, enforces stack depth, interposes the root inode, stores lower dentry/mount, and returns the root.

Unmount uses `ecryptfs_kill_block_super()` to kill the anonymous superblock, put the lower mount, destroy mount crypt state, and free superblock private cache memory.

## Lower File Management
`ecryptfs_get_lower_file()` increments an atomic per-inode count under `lower_file_mutex`; the first reference opens the lower file through `ecryptfs_privileged_open()`. `ecryptfs_put_lower_file()` decrements and, when the last reference drops, writes back the upper mapping, closes the lower file, clears the pointer, and unlocks.

## Cache Management
The file declares and initializes caches for auth-token list items, file info, inode info, superblock info, header buffers, xattr buffers, key records, key signatures, global auth tokens, and key TFMs. Inode cache entries run `inode_init_once()` as constructor. Cache teardown calls `rcu_barrier()` first.

## Module Lifecycle
`ecryptfs_init()` verifies extent size does not exceed page size, initializes caches, registers sysfs, starts the kthread, initializes messaging, initializes crypto, registers the filesystem, and warns if verbosity can leak secrets. Failures unwind in reverse order.

`ecryptfs_exit()` destroys crypto, releases messaging, stops kthread, unregisters sysfs, unregisters filesystem, and frees caches.

## Sysfs
Creates `/sys/fs/ecryptfs/version`, returning `ECRYPTFS_VERSIONING_MASK`.

## Risks and Notes
- FIPS mode disables eCryptfs mounting.
- Mounting on idmapped mounts is explicitly disallowed.
- Recursive eCryptfs-on-eCryptfs mounts are rejected.
- Verbosity above zero can leak secrets.
- Lower-file refcount balance is central to regular-file correctness.
