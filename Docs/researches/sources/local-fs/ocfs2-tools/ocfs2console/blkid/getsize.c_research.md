# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/getsize.c

Computes block device size in bytes for probing code.

Key functions:
- `blkid_get_dev_size(int fd)`
  - Attempts platform-specific ioctls first:
    - Darwin `DKIOCGETBLOCKCOUNT`
    - Linux `BLKGETSIZE64`
    - Linux/compat `BLKGETSIZE`
    - floppy `FDGETPRM`
  - Falls back to binary search over valid seek/read offsets.
- `valid_offset(fd, offset)`
  - Seeks to offset and attempts to read one byte.

Dependencies:
- `blkid_llseek` from `llseek.c`
- platform disk ioctls and headers

Notable details:
- Disables `BLKGETSIZE64` on old Linux 2.x kernels matching a specific release-prefix heuristic.
- Returns `0` on size overflow for too-small `blkid_loff_t`.
- Fallback binary search is slow but portable when no ioctl is available.
