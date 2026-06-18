# File Research: sources/os/bsd/netbsd-src/sys/fs/ntfs/ntfs_inode.h

Defines NTFS in-memory node structures and file-handle layout.

Key contents:
- Inode-style flags for access/change/update state, locking, hashing, loaded attributes, and preloaded directory data.
- `struct ntnode`:
  - Represents an NTFS MFT record.
  - Stores device vnode/dev_t, hash linkage, mount pointer, inode number, flags, lock/cv state, use/busy counters, loaded attribute list, link count, main record, and file-record flags.
- `struct ntkey`:
  - Vnode-cache key combining inode number, attribute type, and variable-length attribute name.
- `struct fnode`:
  - Represents a specific vnode-visible NTFS stream/attribute for an `ntnode`.
  - Stores vnode pointer, associated ntnode, file-name metadata, size/allocation, key storage, and directory enumeration cache.
- `struct ntfid`:
  - File-handle format containing inode and attribute identifier.

Role:
- Separates MFT-record state (`ntnode`) from per-vnode attribute-stream state (`fnode`).
