# File Research: sources/os/linux/linux/fs/9p/v9fs_vfs.h

Declares 9p VFS operation tables and VFS helper functions.

Key behavior:
- Documents 9p create semantics: Plan 9 creates return an opened FID, while Linux separates create and open, so the client tracks the create FID for later open handling.
- Defines `P9_LOCK_TIMEOUT`.
- Defines `V9FS_STAT2INODE_KEEP_ISIZE` for refresh paths that should not overwrite cached file size.
- Declares file, directory, dentry, address-space, superblock, inode, stat conversion, open-mode conversion, refresh, and setattr/fsync helpers.
- Defines `QID2INO()` conversion:
  - On 32-bit, combines high and low QID path bits.
  - On 64-bit, uses `qid.path + 2`.
- `v9fs_invalidate_inode_attr()` marks inode attributes stale through `V9FS_INO_INVALID_ATTR`.

Important interactions:
- Shared by legacy and dotl inode implementations.
- Dentry revalidation uses `V9FS_INO_INVALID_ATTR` to decide whether to refetch attributes.
