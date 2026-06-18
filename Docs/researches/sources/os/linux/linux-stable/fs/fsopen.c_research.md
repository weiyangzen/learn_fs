# File Research: sources/os/linux/linux-stable/fs/fsopen.c

## Purpose
Implements the modern mount API syscalls for creating, configuring, reading diagnostics from, and applying filesystem contexts.

## Key Interfaces
- `fscontext_read()` returns one queued log message per read from an fscontext fd.
- `fscontext_release()` drops the held `fs_context`.
- `fsopen()` opens a filesystem type by name, creates a mount context, allocates a log, and returns an anonymous fd.
- `fspick()` picks an existing mount root for superblock reconfiguration.
- `fsconfig()` validates command/value combinations, imports user parameters, locks the context, and applies configuration or lifecycle commands.
- `vfs_cmd_create()` transitions a creation context through tree construction and mount security checks.
- `vfs_cmd_reconfigure()` locks the target superblock and calls `reconfigure_super()`.

## Design Notes
The fscontext fd is an anonymous inode whose private data owns the `fs_context`. `fc->uapi_mutex` serializes userspace operations. Context phases enforce legal ordering: parameter collection, creating, awaiting mount, reconfiguring, failed, and cleaned states.

## Dependencies
Uses `fs_context`, `fs_parser`, anonymous inodes, fd helpers, VFS path lookup, security hooks, mount internals, and `uapi/linux/mount.h`.

## Research Notes
`fsconfig()` supports flags, strings, binary blobs, paths, empty paths, and fd parameters. It carefully cleans imported user memory unless the filesystem or LSM steals ownership by nulling the parameter pointer.
