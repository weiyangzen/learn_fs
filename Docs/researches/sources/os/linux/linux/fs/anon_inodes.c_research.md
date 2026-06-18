# File Research: sources/os/linux/linux/fs/anon_inodes.c

## Summary
Provides the anonymous-inode pseudo filesystem and helper APIs for kernel subsystems that need file descriptors without persistent filesystem objects.

## Main Responsibilities
- Mount `anon_inodefs` during early fs init.
- Maintain a singleton anonymous inode for normal anon-inode files.
- Allocate secure per-file anonymous inodes when LSM labeling or unique inode identity is needed.
- Create anonymous `struct file` objects and install them into file descriptors.
- Preserve legacy userspace `stat()` behavior for anon inodes.

## Key APIs
- `anon_inode_getfile()`, `anon_inode_getfile_fmode()`.
- `anon_inode_create_getfile()`.
- `anon_inode_getfd()`, `anon_inode_create_getfd()`.
- `anon_inode_make_secure_inode()`.
- `anon_inode_getattr()`, `anon_inode_setattr()`.

## Important Behavior
Normal anon-inode files share one inode, reducing memory and setup overhead. Secure/unique anon-inode creation allocates a fresh inode, clears `S_PRIVATE`, installs anon inode operations, and calls `security_inode_init_security_anon()`.

`anon_inode_getattr()` masks file-type bits from `st_mode` so legacy userspace tools continue to recognize `anon_inode` objects as before.

`__anon_inode_getfile()` pins the file-operations module owner before allocating the file and drops that reference on error.

## Risks
Callers choosing the singleton path share inode identity and security context. Callers needing LSM policy or distinct `fstat()` identity must use the create APIs. The `context_inode` passed to the LSM hook is not refcounted by this helper.
