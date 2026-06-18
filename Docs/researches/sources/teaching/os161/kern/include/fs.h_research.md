# File Research: sources/teaching/os161/kern/include/fs.h

Defines the abstract filesystem object and operation table used by VFS.

Key structures:
- `struct fs` stores filesystem-private data and `fs_ops`.
- `struct fs_ops` contains sync, get volume name, get root vnode, and unmount callbacks.

Key macros:
- `FSOP_SYNC`, `FSOP_GETVOLNAME`, `FSOP_GETROOT`, `FSOP_UNMOUNT`.

Relevance:
- SFS and semfs both embed `struct fs` in their concrete FS structures and fill `fs_ops`.
- Declares `semfs_bootstrap` for built-in fake filesystem initialization.
