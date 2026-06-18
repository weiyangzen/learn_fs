# File Research: sources/os/linux/linux-stable/fs/devpts/inode.c

## Purpose

`inode.c` implements the `devpts` filesystem used for Unix98 PTY slave nodes under `/dev/pts`, including per-instance mount state, `/dev/pts/ptmx`, PTY index allocation, and sysctl limits.

## Main Responsibilities

- Registers the `devpts` filesystem with user-namespace mount support.
- Exposes sysctls under `kernel/pty`: `max`, `reserve`, and `nr`.
- Parses mount options: `uid`, `gid`, `mode`, `ptmxmode`, `newinstance`, and `max`.
- Creates a per-mount root directory and `ptmx` character device node.
- Resolves the correct devpts mount for `/dev/ptmx` opens and bind-mounted `ptmx` cases.
- Allocates and frees PTY indexes with global and per-instance limits.
- Creates and removes slave PTY dentries named by index.
- Stores and retrieves per-PTY private data through `d_fsdata`.

## Core Data Flow

Mount setup:
- `devpts_init_fs_context()` allocates `struct pts_fs_info`, initializes `ida`, default modes, global root uid/gid, max, and reserve behavior for the initial mount namespace.
- `devpts_fill_super()` creates the root directory inode and calls `mknod_ptmx()`.
- `mknod_ptmx()` creates inode number 2 as a `TTYAUX_MAJOR:2` character device with configured `ptmxmode`.

PTY mount acquisition:
- `devpts_acquire()` finds a devpts superblock from a file path or adjacent `pts` directory and increments `s_active`.
- `devpts_release()` drops the superblock reference.
- `devpts_mntget()` validates that a file path corresponds to the expected `pts_fs_info`.

PTY allocation:
- `devpts_new_index()` increments global `pty_count`, enforces reserve and max limits, and allocates an IDA index.
- `devpts_kill_index()` frees the index and decrements global count.
- `devpts_pty_new()` creates a slave character-device inode `UNIX98_PTY_SLAVE_MAJOR:index`, applies configured uid/gid/mode, creates a persistent dentry, and emits fsnotify create.
- `devpts_pty_kill()` clears private data, drops link count, unhashes the dentry, emits fsnotify unlink, and makes it discardable.

## Important Dependencies

- TTY/PTY core code calls the exported devpts helpers.
- VFS simple filesystem helpers and dcache persistent/discardable dentry APIs.
- IDA for per-instance PTY index allocation.
- sysctl infrastructure for global PTY limits.
- `path_pts()` and mount traversal helpers for `/dev/ptmx` resolution.

## Edge Cases and Risks

- Global PTY reserve is preserved for the initial mount namespace; other instances account against `pty_reserve`.
- `ptmxmode` defaults to `0000` to avoid unexpected access in legacy scenarios.
- `devpts_ptmx_path()` only accepts paths rooted at a devpts filesystem mounted as expected.
- PTY count must be decremented when IDA allocation fails or indexes are killed.
- `dentry->d_fsdata` is used for caller private data and must be cleared before removal.
