# File Research: sources/os/linux/linux/fs/fs_context.c

Read status: complete, 568 lines.

Purpose: implements generic VFS filesystem context allocation, mount option parsing, logging, duplication, cleanup, and disposal.

Key flow:
- `vfs_parse_sb_flag()` handles common superblock flags such as `ro/rw`, `sync/async`, `dirsync`, `lazytime/nolazytime`, and `mand/nomand`.
- `vfs_parse_fs_param()` validates parameter names, handles common flags, lets LSMs consume options, delegates to filesystem `parse_param`, and falls back to generic `source`.
- `vfs_parse_fs_qstr()`, `vfs_parse_monolithic_sep()`, and `generic_parse_monolithic()` provide helper paths for qstr and comma-separated legacy mount data.
- `alloc_fs_context()` allocates and initializes `struct fs_context` for mount, submount, or reconfigure, setting fs type refs, credentials, net namespace, user namespace, root references, and filesystem-specific init.
- `fs_context_for_mount()`, `fs_context_for_reconfigure()`, and `fs_context_for_submount()` create purpose-specific contexts.
- `vfs_dup_fs_context()` copies an existing context, takes references, calls filesystem dup, and duplicates security context.
- `logfc()` either printk logs or stores formatted messages in the context ring buffer.
- `put_fs_context()` releases root/superblock, filesystem private state, security options, namespaces, credentials, logs, fs type, source string, and the context allocation.
- `vfs_clean_context()` and `finish_clean_context()` reset a used context into a reconfiguration-ready state in two phases.

Important dependencies: fs parser, LSM mount hooks, net/user namespaces, filesystem `fs_context_operations`, mount lifecycle helpers.

Risk/concurrency notes:
- Context cleanup is split so successful mount/remount can report success before a possibly failing reinitialization.
- `logfc()` uses a fixed-size ring and drops the oldest stored message when full.
