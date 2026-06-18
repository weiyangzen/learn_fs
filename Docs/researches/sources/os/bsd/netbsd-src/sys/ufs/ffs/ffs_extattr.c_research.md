# File Research: sources/os/bsd/netbsd-src/sys/ufs/ffs/ffs_extattr.c

This file implements native UFS2 extended attributes stored in the UFS2 dinode extension block area. UFS1 extended attributes are delegated to the older file-backed UFS extattr implementation when compiled in.

Key responsibilities:
- Read and write UFS2 extended attribute blocks using negative logical block numbers.
- Maintain a per-inode in-memory extended-attribute transaction buffer.
- Implement VOP open/close/get/set/list/delete extended attribute operations.
- Commit EA changes back to `di_extsize`/`di_extb` through `ffs_extwrite` and `ffs_truncate`.
- Route strategy calls for FIFO/native EA negative block numbers.

Important functions:
- `ffs_extread`: Reads the EA data stream from UFS2 extension blocks, using `bread`/`breadn`, EOF clamping, short-read protection, and `uiomove`.
- `ffs_extwrite`: Writes the EA stream, allocating extension blocks with `UFS_BALLOC` and `IO_EXT`, updating `di_extsize`, handling synchronous writes, WAPBL transactions, setuid/setgid clearing, and `IO_UNIT` rollback.
- `ffs_findextattr`: Walks packed `struct extattr` records and matches namespace/name, returning content size and optional record/content pointers.
- `ffs_rdextattr`: Allocates a temporary contiguous copy of the EA area and fills it with `ffs_extread`.
- `ffs_open_ea` / `ffs_close_ea`: Reference-count the in-memory EA area, commit or discard changes, truncate stale on-disk extension data when the new EA area shrinks, and free state on last close.
- `ffsext_strategy`: Sends UFS2 negative EA logical blocks to `ufs_strategy`; FIFO non-EA traffic bypasses to FIFO handling.
- `ffs_getextattr`: Checks credentials, opens the EA transaction, finds a named attribute, and either returns its size or copies content to the caller.
- `ffs_setextattr`: Builds or replaces an aligned `struct extattr` record, grows/shrinks the in-memory packed area, copies user data, and commits.
- `ffs_listextattr`: Emits namespace-filtered attribute names in extattr list format.
- `ffs_deleteextattr`: Removes a named record by compacting the packed EA area and committing.

Important interactions:
- Uses UFS2 `di_extsize` and `di_extb[]`; rejects native EA operations on UFS1 unless `UFS_EXTATTR` fallback exists.
- Uses `extattr_check_cred` for namespace permission checks.
- Uses `genfs_node_wrlock` to serialize EA buffer state.
- Uses WAPBL around EA writes and truncation.

Notable behavior and risks:
- EA records are manually packed and 8-byte padded; malformed lengths can stop scans early.
- Commit truncates the entire EA stream to zero before rewriting when shrinking, noted by an in-code XXX.
- `ffs_setextattr` rejects NULL `uio` deletion; deletion is handled by `ffs_deleteextattr`.
- Device nodes are rejected for some native EA paths.
