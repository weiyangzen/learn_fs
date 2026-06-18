# File Research: sources/local-fs/ocfs2-tools/ocfs2console/blkid/llseek.c

Portable large-file seek wrapper for blkid probing.

Key function:
- `blkid_llseek(int fd, blkid_loff_t offset, int whence)`
  - Uses plain `lseek` when `off_t` can represent the offset.
  - Uses `lseek64`, `llseek`, or Linux `_llseek` syscall depending on platform/configure probes.
  - On unsupported large offsets, sets `errno = EOVERFLOW`.

Dependencies:
- Linux syscall support when no direct 64-bit seek wrapper exists.
- `blkid_loff_t` from public blkid types.

Notable details:
- Maintains `do_compat` static flag after `ENOSYS` to avoid repeated unsupported syscall attempts.
- Non-Linux path falls back to `lseek64` when available or guarded `lseek`.
