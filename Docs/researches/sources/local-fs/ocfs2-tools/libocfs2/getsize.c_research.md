# File Research: sources/local-fs/ocfs2-tools/libocfs2/getsize.c

Purpose: determines block-device or file size in filesystem blocks.

Key API:
- `ocfs2_get_device_size()`

Platform behavior:
- On Windows/Cygwin, uses `CreateFile()`, partition info, disk geometry, or file size APIs.
- On Unix-like systems, opens read-only with `open64()` when available.
- Supports Darwin `DKIOCGETBLOCKCOUNT`.
- Supports Linux `BLKGETSIZE64`, with a guard against early 2.6 kernel releases, then `BLKGETSIZE`.
- Supports floppy `FDGETPRM`.
- Supports BSD disklabel/media-size ioctls when available.
- Falls back to `fstat64()`/`fstat()` for regular files.
- Last fallback uses binary search with `lseek64()` and one-byte reads to discover the final valid offset.

Core invariants:
- Returned value is `size / blocksize`.
- Some platform branches check for overflow into smaller `retblocks` types and return `EFBIG`.
- File descriptor is closed through the `out` path in normal Unix branches.

Dependencies:
- Platform ioctl headers and stat APIs.
- OCFS2 error integration is light; many failures return raw `errno`.

Notable behavior and risks:
- Some early returns in ioctl overflow checks return `EFBIG` before the common close path in the Unix implementation.
- Binary-search fallback can be expensive on unusual devices but provides broad compatibility.
