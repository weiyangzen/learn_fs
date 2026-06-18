# File Research: sources/os/linux/linux-stable/fs/read_write.c

## Purpose
Implements generic VFS read, write, seek, vector I/O, sendfile, copy_file_range, and common write/copy validation helpers.

## Major Areas
- Generic read-only file operations via `generic_ro_fops`.
- Seek helpers: `vfs_setpos`, `generic_file_llseek_size`, `generic_llseek_cookie`, `generic_file_llseek`, fixed/no-end/noop/default seek implementations, `vfs_llseek`, and lseek syscalls.
- Access validation: `rw_verify_area()` combines offset/count checks, LSM permission checks, and fsnotify permission hooks.
- Scalar I/O: `vfs_read`, `vfs_write`, `kernel_read`, `kernel_write`, `ksys_read`, `ksys_write`, `pread64`, `pwrite64`.
- Iter/vector I/O: `vfs_iter_read`, `vfs_iter_write`, `vfs_iocb_iter_read`, `vfs_iocb_iter_write`, `readv`, `writev`, `preadv`, `pwritev`, `preadv2`, `pwritev2`, plus compat variants.
- `sendfile`: implements splice-based file-to-file or file-to-pipe transfer.
- `copy_file_range`: validates ranges, tries filesystem copy, same-superblock clone, or splice fallback.
- Write validation: `generic_write_check_limits`, `generic_write_checks_count`, `generic_write_checks`, `generic_file_rw_checks`, and `generic_atomic_write_valid`.

## Important Semantics
- Clamps I/O to `MAX_RW_COUNT`.
- Uses `file_start_write()` / `file_end_write()` for write paths.
- Updates task I/O accounting and fsnotify access/modify events on success.
- Handles `FMODE_STREAM` by avoiding `f_pos`.
- Provides fallback looped `read`/`write` support for vector I/O when iter ops are unavailable.
- Enforces `RLIMIT_FSIZE`, `O_LARGEFILE`, max file size, swapfile restrictions, append restrictions, and overlap restrictions for copy operations.

## Edge Cases
- `SEEK_DATA` / `SEEK_HOLE` generic behavior treats the whole file as data and EOF as a virtual hole.
- `copy_file_range()` avoids unsafe cross-filesystem filesystem callbacks unless explicitly using splice.
- Atomic writes require ubuf iter, power-of-two length, position alignment, and direct I/O.
