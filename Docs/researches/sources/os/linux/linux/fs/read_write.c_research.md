# File Research: sources/os/linux/linux/fs/read_write.c

Core VFS read/write, seek, vector IO, sendfile, copy_file_range, and generic write/copy validation implementation.

Key responsibilities:
- Defines `generic_ro_fops`, a read-only generic file-operations table.
- Implements generic seek helpers:
  - `vfs_setpos()`
  - `generic_file_llseek_size()`
  - `generic_llseek_cookie()`
  - `generic_file_llseek()`
  - `fixed_size_llseek()`
  - `no_seek_end_llseek()`
  - `noop_llseek()`
  - `default_llseek()`
  - `vfs_llseek()`
- Implements seek syscalls:
  - `lseek`
  - compat `lseek`
  - `llseek` where required.
- Validates read/write access with `rw_verify_area()`, including offset overflow, LSM permission, and fsnotify area permission.
- Implements kernel internal reads/writes:
  - `__kernel_read()`
  - `kernel_read()`
  - `__kernel_write_iter()`
  - `__kernel_write()`
  - `kernel_write()`
- Implements user scalar IO:
  - `vfs_read()`
  - `vfs_write()`
  - `ksys_read()` / `read`
  - `ksys_write()` / `write`
  - `pread64`
  - `pwrite64`
- Implements vector and positioned vector IO:
  - `vfs_iocb_iter_read()`
  - `vfs_iter_read()`
  - `vfs_iocb_iter_write()`
  - `vfs_iter_write()`
  - `readv`, `writev`, `preadv`, `pwritev`, `preadv2`, `pwritev2`
  - compat variants.
- Implements sendfile with `do_sendfile()`, `sendfile`, `sendfile64`, and compat variants.
- Implements `vfs_copy_file_range()` and `copy_file_range` syscall.
- Provides generic write/copy validation:
  - `generic_write_check_limits()`
  - `generic_write_checks_count()`
  - `generic_write_checks()`
  - `generic_file_rw_checks()`
  - `generic_atomic_write_valid()`

Important behavior:
- Caps user IO sizes at `MAX_RW_COUNT`.
- Uses `file_start_write()` / `file_end_write()` around write paths and copy paths as needed.
- Updates task accounting (`add_rchar`, `add_wchar`, `inc_syscr`, `inc_syscw`) and fsnotify events on successful IO.
- Uses local position copies for normal read/write syscalls so position updates occur only after successful VFS calls.
- Supports `preadv2` / `pwritev2` with `pos == -1` as current-position vector IO.
- `copy_file_range` first tries filesystem `copy_file_range`, then same-superblock remap/clone, then splice fallback where allowed.
- `generic_copy_file_checks()` rejects immutable output, swapfiles, overflowed offsets, overlapped same-file copies, and cross-superblock cases unless an allowed path exists.
- `generic_write_check_limits()` enforces `RLIMIT_FSIZE`, `O_LARGEFILE`, superblock max bytes, and sends `SIGXFSZ` when appropriate.
- `generic_atomic_write_valid()` requires user buffer iterator, power-of-two length, aligned offset, and direct IO.

Research notes:
- This file is a major syscall-to-filesystem adaptor. Filesystems implement lower-level `file_operations`; this file supplies common validation, accounting, fallback, and syscall glue.
