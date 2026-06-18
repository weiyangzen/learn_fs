# File Research: sources/os/linux/linux/fs/hostfs/hostfs_user.c

Purpose: Implements host-side syscall wrappers used by UML hostfs kernel code.

Key functions:
- `statx_to_hostfs()` converts Linux `statx` results into `struct hostfs_stat`.
- `stat_file()` uses `statx()` with `AT_SYMLINK_NOFOLLOW` and optional `AT_EMPTY_PATH`.
- `access_file()`, `open_file()`, `read_file()`, `write_file()`, `lseek_file()`, `fsync_file()`, and `replace_file()` wrap host file operations and return negative errno.
- Directory wrappers use `opendir()`, `seekdir()`, `readdir()`, and `closedir()`.
- Creation/mutation wrappers cover `open64(O_CREAT)`, chmod/chown/truncate, symlink, unlink, mkdir, rmdir, mknod, hardlink, readlink, rename, and renameat2.
- `do_statfs()` wraps `statfs64()` and copies statfs fields to caller-provided outputs.

Dependencies and integration:
- Consumed by `hostfs_kern.c`; exported via `hostfs_user_exp.c`.
- Uses libc/syscall interfaces from the UML host process environment.

Risk notes:
- Most wrappers return raw negative host errno, so kernel-side callers depend on host errno semantics.
- `rename2_file()` supports `renameat2` only when syscall numbers are known or present; otherwise it returns `-EINVAL`.
- `set_attr()` does not set ctime directly and uses microsecond `utimes`/`futimes` precision for atime/mtime.
