# File Research: sources/teaching/minix/minix/servers/vfs/link.c

This file implements link, unlink, rename, truncate, symlink, and readlink operations.

Key functions:
- `do_link`: creates hard links.
- `do_unlink`: handles unlink and rmdir.
- `do_rename`: renames paths.
- `do_truncate`: truncates by path.
- `do_ftruncate`: truncates by descriptor.
- `truncate_vnode`: shared truncation helper.
- `do_slink`: creates symlinks.
- `rdlink_direct`: VFS-internal readlink helper.
- `do_rdlink`: readlink syscall.

Important behavior:
- Hard links must remain within the same filesystem endpoint.
- Unlink/rmdir require directory write and execute permission.
- Sticky directories require file ownership or superuser for unlink/rename.
- Rename locks old and new parent directories and upgrades the old mount lock before issuing `req_rename`.
- Truncate avoids filesystem calls when regular-file size is unchanged for POSIX timestamp behavior.
- `truncate_vnode` allows regular files and FIFOs.
- Symlink creation validates target length and uses `req_slink`.
- Readlink uses `PATH_RET_SYMLINK` to resolve the link itself rather than the target.

Important interactions:
- Relies heavily on path lookup helpers (`fetch_name`, `copy_path`, `last_dir`, `eat_path`, `advance`) and filesystem request calls (`req_link`, `req_unlink`, `req_rmdir`, `req_rename`, `req_ftrunc`, `req_slink`, `req_rdlink`).
