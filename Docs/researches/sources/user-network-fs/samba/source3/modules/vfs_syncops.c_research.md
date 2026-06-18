# sources/user-network-fs/samba/source3/modules/vfs_syncops.c

## Purpose

`vfs_syncops.c` is a durability-focused Samba VFS module that forces metadata and close-time synchronization after operations that create, remove, or rename directory entries. It is intended for filesystems or clustered deployments where Samba must ensure metadata survives power loss or failover. The module registers as `syncops`.

## Important APIs, Types, And Functions

`struct syncops_config_data` stores three booleans: `onclose`, `onmeta`, and `disable`. `parent_dir()` computes the parent path string for a name. `syncops_sync_directory()` opens a directory through Samba's `OpenDir()` and calls `smb_vfs_fsync_sync()` on the directory FSP. `syncops_two_names()` syncs both parent directories for operations involving source and destination paths, while `syncops_smb_fname()` syncs one parent directory.

The `SYNCOPS_NEXT_SMB_FNAME` macro wraps simple metadata operations by calling the next VFS function, checking config, constructing a full path from `dirfsp` and `smb_fname`, syncing the parent directory, and returning the original result. Explicit wrappers handle `renameat`, `linkat`, `openat`, `unlinkat`, `mknodat`, `mkdirat`, `symlinkat`, and `close`.

## Control Flow

On connect, the module calls the next connect hook, allocates config, and reads `syncops:onclose` (default true), `syncops:onmeta` (default true), and `syncops:disable` (default false). Metadata wrappers first perform the requested operation through the next VFS module. If it fails, or if syncops is disabled, or if `onmeta` is false, they return immediately. Otherwise they derive full paths and fsync the affected parent directories. `renameat` and `linkat` explicitly handle two directory names; create-like and delete-like operations use the shared macro. `close` fsyncs the file descriptor before closing when the file can be written and `onclose` is enabled.

## State And Persistence

The module has no durable private state. It intentionally changes persistence behavior of underlying filesystems by invoking fsync on files and directories. Config is per VFS handle/share connection and is talloc-managed with the connection.

## Dependencies And Integration Points

The module uses Samba directory helpers from `source3/smbd/dir.h`, path construction via `full_path_from_dirfsp_atname()`, and the core VFS operation chain. It is listed in `source3/modules/wscript_build` and appears in `source3/wscript` default shared modules for non-static builds.

## Risks And Edge Cases

The major risk is performance: fsync on close and parent-directory fsync after metadata changes can dominate workload latency. Some error paths intentionally return the original successful metadata result even if path construction or sync fails, so durability can silently degrade under memory pressure or directory-open failures. Parent path calculation is string-based and assumes normalized names. The `mkdirat` wrapper passes an unused macro parameter expression, but the macro body uses `smb_fname` directly, so this is confusing but not functionally significant.

## Test Signals

Tests should verify that each metadata operation delegates correctly when disabled, that configured `onmeta=no` and `onclose=no` suppress sync behavior, and that rename/link sync both parent directories when source and destination differ. Fault injection around `OpenDir()`, path construction, and fsync would validate that user-visible operation status is preserved while durability warnings can be diagnosed through debug logs.
