# File Research: sources/os/linux/linux-stable/fs/fs_context.c

This file implements the VFS filesystem context abstraction used for mounting, submounting, remount/reconfigure, option parsing, logging, duplication, and cleanup.

Major responsibilities:
- Parse common superblock flags such as `ro`, `rw`, `sync`, `async`, `dirsync`, `lazytime`, and `mand`.
- Parse a generic `source` parameter when accepted by the filesystem.
- Route mount parameters through common VFS parsing, LSM parsing, filesystem-specific parsing, and source fallback.
- Parse monolithic comma-separated mount option strings.
- Allocate filesystem contexts for mounts, submounts, and reconfiguration.
- Duplicate contexts through filesystem and LSM hooks.
- Store context log messages in a bounded ring buffer or print directly.
- Free contexts, security options, namespace references, credentials, source strings, logs, and filesystem references.
- Clean a used context into an awaiting-reconfiguration state and lazily finish reinitialization.

Important design points:
- `fs_context` captures filesystem type, credentials, net namespace, user namespace, root dentry for reconfigure, superblock flags, security state, source, and filesystem-private state.
- Mount contexts use the caller's user namespace; submount and reconfigure contexts inherit from the referenced superblock.
- Parameter parsing first handles VFS-wide flags, then lets LSMs consume or reject options before filesystem parsing.
- `vfs_dup_fs_context()` copies the structure but resets owned private pointers before calling filesystem `dup()` and LSM duplication.
- `vfs_clean_context()` intentionally performs only non-failing cleanup after a successful mount/reconfigure and defers fallible reinitialization to `finish_clean_context()`.

Key invariants:
- `fc->fs_type` holds a filesystem module reference until `put_fs_context()`.
- `fc->root` pins an active superblock for reconfiguration and is released through `deactivate_super()` or `deactivate_locked_super()`.
- `fc->need_free` controls whether filesystem-specific `ops->free()` is called.
- `fc->source` ownership is transferred from `fs_parameter` by nulling `param->string`.
- Unknown parameters become contextual `invalf()` errors after VFS, LSM, filesystem, and source parsing decline them.

External interfaces:
- Exports parsing helpers, context allocation helpers, duplication, logging, and `put_fs_context()`.
- Used by modern mount APIs and filesystem `init_fs_context` implementations.
