# File Research: sources/os/linux/linux-stable/fs/ecryptfs/file.c

## Summary
Implements eCryptfs file and directory operations. It opens and tracks lower files, initializes or reads encryption metadata, wraps read/readdir behavior for lower atime and filename decryption, forwards selected ioctls, and delegates mmap/fsync/flush/fasync behavior to lower files where appropriate.

## Main Responsibilities
- Wrap regular reads and splice reads so successful upper reads update lower atime.
- Implement directory iteration by decoding/decrypting lower names before emitting them.
- Open regular files, acquire the shared lower file, enforce lower read-only constraints, and load or initialize metadata.
- Open directories directly on the lower path.
- Support plaintext passthrough and empty-file initialization behavior when metadata is absent.
- Forward supported ioctls and compat ioctls to lower files: FITRIM, flags, and version ioctls.
- Synchronize writes and lower flush/fsync operations.
- Define regular-file and directory `file_operations`.

## Key APIs
- `ecryptfs_open()`
- `ecryptfs_dir_open()`
- `ecryptfs_readdir()`
- `read_or_initialize_metadata()`
- `ecryptfs_main_fops`
- `ecryptfs_dir_fops`

## Important Behavior
`read_or_initialize_metadata()` first tries to parse eCryptfs metadata. If that fails, plaintext passthrough can allow a non-encrypted lower file. If xattr metadata is not enabled and the lower file is empty, eCryptfs initializes it as an encrypted file by writing headers.

Directory reads mask `-EINVAL` filename-decryption failures, allowing plaintext lower names such as `lost+found` to be skipped rather than breaking the entire directory listing when filename encryption is enabled.

Regular file open shares a single lower `struct file` per upper inode via `ecryptfs_get_lower_file()`. Directory open uses a separate `dentry_open()` for each directory file.

## Research Notes
This file is the regular VFS file-operation layer. It relies on `crypto.c` for metadata and filename decoding, `main.c` for lower-file lifetime, and `inode.c` for upper/lower inode mapping.
