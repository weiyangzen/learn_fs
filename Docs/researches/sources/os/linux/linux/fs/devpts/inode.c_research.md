# File Research: sources/os/linux/linux/fs/devpts/inode.c

## Role

Implements the devpts pseudo-filesystem used for Unix98 PTY slave nodes under `/dev/pts`, including mount options, per-instance PTY allocation, `ptmx` support, and PTY node creation/removal.

## Major Responsibilities

- Registers the `devpts` filesystem.
- Parses mount options for ownership, permissions, ptmx mode, new instances, and PTY limits.
- Creates the root directory and `ptmx` character device node.
- Tracks allocated PTY indexes per devpts instance.
- Provides APIs used by TTY/PTY code to create and remove slave nodes.
- Maintains global PTY sysctls under `kernel/pty`.

## Global PTY Limits

Sysctls:

- `kernel/pty/max`
- `kernel/pty/reserve`
- `kernel/pty/nr`

State:

- `pty_limit`
- `pty_reserve`
- `pty_count`

`devpts_new_index()` enforces global reserve behavior and per-instance maximum index allocation through an `ida`.

`devpts_kill_index()` frees the index and decrements the global count.

## Mount Options

Parsed options:

- `uid`
- `gid`
- `mode`
- `ptmxmode`
- `newinstance`
- `max`

Stored in `struct pts_mount_opts`.

Defaults:

- Slave mode: `0600`
- `ptmx` mode: `0000`
- uid/gid: global root
- max: `NR_UNIX98_PTY_MAX`

The initial mount namespace gets reserved PTY capacity by default.

## Per-Superblock State

`struct pts_fs_info` stores:

- `allocated_ptys` IDA.
- Mount options.
- Owning superblock.
- Borrowed `ptmx_inode`.

`DEVPTS_SB()` retrieves this state from `super_block->s_fs_info`.

## Locating the Correct devpts Instance

`devpts_mntget()` and `devpts_acquire()` support PTY code that starts from an opened `ptmx` file and needs the matching devpts filesystem.

They handle cases where `ptmx` is inside `/dev/pts` or is a bind mount / symlink-like external entry that must resolve to a sibling `pts` mount.

`devpts_release()` drops the active superblock reference.

## Superblock Setup

`devpts_fill_super()`:

- Allows device nodes by clearing `SB_I_NODEV`.
- Sets block size and magic.
- Installs simple super operations.
- Marks dentries `DCACHE_DONTCACHE`.
- Creates root directory inode.
- Creates root dentry with `d_make_root()`.
- Calls `mknod_ptmx()` to create the `ptmx` char device.

`mknod_ptmx()` creates `ptmx` as character device `TTYAUX_MAJOR:2`, persists it with `d_make_persistent()`, and records the inode in `pts_fs_info`.

`devpts_reconfigure()` updates mount options on remount and updates `ptmx` mode.

## Filesystem Registration

`devpts_fs_type`:

- Name: `devpts`
- Uses fs_context operations.
- Supports user namespace mounts via `FS_USERNS_MOUNT`.
- Uses `kill_anon_super()` through `devpts_kill_sb()`.

`init_devpts_fs()` registers the filesystem and PTY sysctls.

## PTY Node Lifecycle

`devpts_pty_new()`:

- Creates a new inode for the slave device.
- Names it by decimal PTY index.
- Applies uid/gid from mount options or current fsuid/fsgid.
- Creates character device `UNIX98_PTY_SLAVE_MAJOR:index`.
- Allocates a dentry under the root.
- Stores caller private data in `dentry->d_fsdata`.
- Persists the dentry with `d_make_persistent()`.
- Sends fsnotify create.
- Drops the local dentry reference and returns a borrowed dentry.

`devpts_get_priv()` returns the stored private pointer for devpts dentries.

`devpts_pty_kill()`:

- Clears `d_fsdata`.
- Drops inode link count.
- Drops the dentry from lookup.
- Sends unlink notification.
- Makes the persistent dentry discardable.

## Important Invariants

- Each devpts mount has independent PTY index allocation.
- Global `pty_count` protects system-wide resource limits.
- `ptmx` is created per devpts instance.
- PTY dentries are persistent while active and discarded on `devpts_pty_kill()`.
- The returned dentry from `devpts_pty_new()` is documented as borrowed.

## Research Notes

This file is a small pseudo-filesystem built on simple VFS primitives and the dcache persistent/discardable API. The main correctness concerns are mount-instance selection, PTY limit accounting, and persistent dentry cleanup.
