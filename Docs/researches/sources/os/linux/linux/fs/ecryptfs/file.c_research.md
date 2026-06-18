# File Research: sources/os/linux/linux/fs/ecryptfs/file.c

## Purpose
Implements eCryptfs file operations for regular files and directories, including open/release, read atime propagation, directory iteration with filename decryption, mmap, fsync, flush, async notification, and selected ioctl forwarding.

## Main Responsibilities
- Attach per-open `ecryptfs_file_info` and lower files.
- Read or initialize crypto metadata on regular-file open.
- Decode and decrypt lower directory names before emitting them upward.
- Forward allowed ioctls and file attributes to lower files.
- Keep lower atime and upper attributes synchronized.

## Key Control Flow
Regular `ecryptfs_open()` allocates file-private state, applies default policy flags if needed, obtains the shared lower file through `ecryptfs_get_lower_file()`, rejects write access if the lower file is read-only, stores the lower file pointer, and calls `read_or_initialize_metadata()`.

`read_or_initialize_metadata()` locks `crypt_stat->cs_mutex`, returns if policy and key are already valid, otherwise tries `ecryptfs_read_metadata()`. If metadata is absent and plaintext passthrough is enabled, it clears initialized-size/encrypted flags. If metadata is absent, xattr metadata is disabled, and the lower file is empty, it initializes a new eCryptfs file.

Directory `ecryptfs_readdir()` wraps `iterate_dir()` with `ecryptfs_filldir()`. Each lower name is decoded/decrypted; `-EINVAL` decode failures are masked so plaintext lower entries such as `lost+found` can be skipped/ignored gracefully under filename encryption.

## File Operations
`ecryptfs_main_fops` uses generic read/write paths through the eCryptfs address-space operations, custom open/release/flush/fsync/mmap/fasync, and splice read with lower atime update.

`ecryptfs_dir_fops` provides directory iteration, generic directory read, open/release, fsync, llseek, and ioctl forwarding.

## Dependencies
- Crypto metadata functions from `crypto.c`.
- Lower-file refcounting from `main.c`.
- Filename decode from `crypto.c`/`keystore.c`.
- VFS generic file helpers and lower file operations.

## Error Handling and Edge Cases
- `mmap` is refused if the lower file cannot be mmaped.
- Only selected ioctls are forwarded: trim, flags, and version get/set variants.
- Open failure frees file-private cache allocation and releases lower-file references.
- Directory open uses a direct `dentry_open()` rather than the shared regular-file lower-file cache.

## Risks and Notes
- The lower file is shared per inode for regular files, so correctness depends on balanced `ecryptfs_get_lower_file()`/`ecryptfs_put_lower_file()`.
- Filename-decryption failures can hide lower entries from directory output when they are not valid encrypted eCryptfs names.
