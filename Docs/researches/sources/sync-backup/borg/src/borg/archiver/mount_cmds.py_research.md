# sources/sync-backup/borg/src/borg/archiver/mount_cmds.py

## Purpose

`mount_cmds.py` implements `borg mount`, `borg umount`, and `borgfs` parser setup for exposing a repository or archive as a FUSE filesystem. It validates mount prerequisites, selects the available FUSE backend, and wires mount-specific archive/path/filter options. The source was read as a complete 196-line file.

## Important APIs, Types, and Functions

`MountMixIn.do_mount()` performs pre-repository FUSE and mountpoint checks. `_do_mount()` opens the repository for read and dispatches to either `hlfuse.borgfs` when `has_mfusepy` is true or `fuse.FuseOperations` otherwise. `do_umount()` calls the platform `umount()` helper. `build_parser_mount_umount()` registers `mount` and `umount`, `build_parser_borgfs()` configures the standalone `borgfs` entrypoint, and `_define_borg_mount()` adds shared mount arguments.

## Control Flow

`do_mount()` imports FUSE capability flags, raises `RTError` if no backend exists, checks that the mountpoint is an existing writable directory, then calls `_do_mount()`. `_do_mount()` creates backend operations with the manifest, args, and repository, logs mounting, and invokes `operations.mount()` with mountpoint, options, foreground, and show-rc settings. Runtime errors are converted into `RTError("FUSE mount failed")`. `umount` delegates to platform unmount logic.

## State and Persistence Behavior

Mounting creates a live FUSE mount and usually daemonizes unless `--foreground` is set. It does not mutate repository data. Unmounting mutates OS mount state. The mounted view loads archive directory data on demand and may consume memory cache in the FUSE layer.

## Dependencies and Integration Points

The module integrates with `fuse_impl` backend selection, `hlfuse`/`fuse` operations, manifest/archive filtering, path matching/exclusion groups, platform unmount helpers, and mount options such as `versions`, `allow_damaged_files`, `ignore_permissions`, `uid`, and `gid`. It exposes the same option set through both `borg mount` and `borgfs`.

## Risks and Edge Cases

Mount checks happen before passphrase prompts to fail fast. Missing FUSE support, nonexistent mountpoints, or insufficient permissions stop the command. Symlinks inside archives can point outside the mountpoint when followed by users. Daemon crashes do not automatically unmount, and foreground mode handles SIGINT more cleanly. Backend differences between mfusepy and llfuse/pyfuse3 can change behavior.

## Test Signals

Tests should mock no-FUSE and each backend path, validate mountpoint existence and access checks, assert mount argument propagation, cover RuntimeError translation, verify `borgfs` parser setup, and smoke-test unmount delegation. Integration tests need actual FUSE support and should cover foreground/background behavior and path-filtered archive mounts.
