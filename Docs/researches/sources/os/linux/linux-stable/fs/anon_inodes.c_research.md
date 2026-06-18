# File Research: sources/os/linux/linux-stable/fs/anon_inodes.c

## Purpose
Provides the anonymous-inode filesystem and helper APIs used by kernel subsystems to create file objects or file descriptors that are not backed by ordinary filesystem paths.

## Main Interfaces
- `anon_inode_getfile()`, `anon_inode_getfile_fmode()`.
- `anon_inode_create_getfile()`.
- `anon_inode_getfd()`, `anon_inode_create_getfd()`.
- `anon_inode_make_secure_inode()`.
- `anon_inode_getattr()` and `anon_inode_setattr()` for anonymous inode stat behavior.

## Important Behavior
Most anonymous files share a singleton inode to avoid per-file inode overhead. Callers that need a unique inode or LSM security context use the `create` variants, which allocate a non-`S_PRIVATE` inode and call `security_inode_init_security_anon()`.

The custom `getattr` masks off file-type bits in `st_mode` to preserve historical userspace detection of `anon_inode`. File creation takes a module reference for `fops->owner`, allocates a pseudo file on the `anon_inodefs` mount, sets `private_data`, and exposes the file through `FD_ADD()` when an fd is requested.

## Cross-File Relationships
Backs common kernel APIs such as eventfd/epoll-like anonymous files and security-sensitive consumers needing `anon_inode_create_*`. It uses the VFS pseudo filesystem helpers and LSM anonymous-inode initialization hook.

## Risks / Review Notes
The shared singleton inode path intentionally skips per-object security initialization. Callers needing LSM policy or unique stat identity must choose the secure create path. Module owner refs and inode/file cleanup are paired in the common helper.
