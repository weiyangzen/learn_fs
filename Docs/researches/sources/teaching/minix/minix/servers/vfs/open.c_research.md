# File Research: sources/teaching/minix/minix/servers/vfs/open.c

Implements open, create, node creation, directory creation, seek, and close operations.

Key behavior:
- `do_open` rejects `O_CREAT` and calls `common_open`; `do_creat` requires `O_CREAT`, fetches the pathname and mode, then calls `common_open`.
- `common_open` allocates an fd and filp, resolves or creates a vnode, installs the filp, applies `O_CLOEXEC`, enforces permissions, and dispatches based on vnode type.
- Regular files may be truncated with `O_TRUNC` after a write-permission check.
- Directories are openable for read but not write.
- Character devices call `cdev_open`; block devices call `bdev_open`, set `v_bfs_e` based on mounted filesystems, and notify the root FS about driver labels when needed.
- FIFOs are mapped to PipeFS with `map_vnode`, forced to append mode, and opened through `pipe_open`; shared reader/writer filps may be reused.
- Sockets cannot be opened from regular path opens and return `EOPNOTSUPP`.

Creation helpers:
- `new_node` resolves the parent with `last_dir`, handles `O_EXCL` symlink behavior, creates regular files with `req_create`, and handles dangling symlinks by reading the link and recursively creating at the target.
- `do_mknod` supports special nodes and FIFOs, with non-FIFO creation restricted to superuser.
- `do_mkdir` resolves the parent and calls `req_mkdir`.

Seek/close:
- `actual_lseek` rejects pipes, computes `SEEK_SET/CUR/END`, checks offset overflow, updates filp position, and inhibits FS read-ahead on position changes.
- `close_fd` removes the fd before closing the filp to prevent concurrent closes, clears close-on-exec, and releases advisory locks owned by the process.

Notable details:
- `mode_map` translates `O_ACCMODE` to filp permission bits.
- Error cleanup distinguishes suspended FIFO opens from normal failures.
- `common_open` installs the filp before device/FIFO open so lower layers can clone or suspend against the fd.
