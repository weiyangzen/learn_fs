# File Research: sources/os/linux/linux/fs/fsopen.c

## Purpose
This file implements the fd-based mount API system calls `fsopen`, `fspick`, and `fsconfig`. It exposes filesystem contexts as anonymous-inode file descriptors, lets userspace read context log messages, set parameters, create mount trees, and reconfigure existing superblocks.

## Main Definitions
- `fscontext_fops` provides `.read` for log retrieval and `.release` for `put_fs_context()`.
- `fscontext_create_fd()` wraps an `fs_context` in an anonymous inode fd.
- `fscontext_alloc_log()` allocates the per-context log buffer.
- `SYSCALL_DEFINE2(fsopen)` opens a filesystem type for new mount configuration.
- `SYSCALL_DEFINE3(fspick)` selects an existing mount root for reconfiguration.
- `vfs_cmd_create()` transitions a creation context through tree creation and security checks.
- `vfs_cmd_reconfigure()` applies reconfiguration to an existing superblock.
- `SYSCALL_DEFINE5(fsconfig)` validates and imports one parameter/action from userspace.

## Control Flow And Behavior
`fsopen()` requires `may_mount()`, accepts only `FSOPEN_CLOEXEC`, resolves the filesystem type by name, creates a mount `fs_context`, moves it to `FS_CONTEXT_CREATE_PARAMS`, allocates logging, and returns an fd.

`fspick()` requires `may_mount()`, resolves a path with flags controlling symlink follow, automount, and empty path behavior, requires that the selected dentry is the mount root, creates a reconfiguration context, moves it to `FS_CONTEXT_RECONF_PARAMS`, allocates logging, and returns an fd.

`fsconfig()` validates the command-specific shape of `_key`, `_value`, and `aux`; imports strings, binary blobs, filenames, paths, or fds into a `struct fs_parameter`; locks `fc->uapi_mutex`; then calls `vfs_fsconfig_locked()`. Create/reconfigure commands drive phase transitions; ordinary set commands call `vfs_parse_fs_param()`. Imported values are cleaned up unless stolen by filesystem or LSM code.

## Dependencies And Interfaces
This file depends on `fs_context`, `fs_parser`, mount internals, anonymous inodes, name lookup, fd helpers, security hooks, and UAPI mount command constants.

## Concurrency And Safety
`fc->uapi_mutex` serializes userspace API operations against one context and protects log reads. Phase checks prevent reusing a context after creation/reconfiguration has progressed. `vfs_cmd_create()` releases `s_umount` after `vfs_get_tree()` succeeds because lower call chains acquired it.

## Research Notes
The file is the userspace entry point for the modern mount API. Important constraints include 256-byte limits for keys/strings, a 1 MiB binary parameter cap, exclusive phase states, and fd type checking against `fscontext_fops`.
