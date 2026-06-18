# File Research: sources/os/linux/linux/fs/fuse/control.c

## Purpose
This file implements the `fusectl` control filesystem. It exposes per-FUSE-connection control and status files under a single in-kernel pseudo filesystem, including abort, waiting request count, and background request throttling knobs.

## Main Definitions
- `fuse_control_sb` tracks the single mounted control superblock, protected by `fuse_mutex`.
- `fuse_ctl_file_conn_get()` obtains a referenced `fuse_conn` from a control file inode.
- Control file operations:
  - `abort`: write-only, aborts the connection.
  - `waiting`: read-only, reports `fc->num_waiting`.
  - `max_background`: read/write, controls `fc->max_background`.
  - `congestion_threshold`: read/write, controls `fc->congestion_threshold`.
- `fuse_ctl_add_dentry()` creates persistent dentries/inodes under the control fs.
- `fuse_ctl_add_conn()` creates a per-connection directory and files.
- `fuse_ctl_remove_conn()` removes a connection directory.
- `fuse_ctl_fill_super()` initializes the singleton superblock and populates existing connections.
- `fuse_ctl_fs_type` registers filesystem name `fusectl`.

## Control Flow And Behavior
When `fusectl` is mounted, `simple_fill_super()` creates the root and `fuse_ctl_fill_super()` records the superblock as the singleton. It then iterates `fuse_conn_list` and creates one directory per connection named by `fc->dev`. New connections can be added later through `fuse_ctl_add_conn()`.

Writes to limits parse unsigned values from userspace. Without `CAP_SYS_ADMIN`, requested limits are capped by global user limits (`max_user_bgreq` and `max_user_congthresh`). Updating `max_background` also updates `fc->blocked` and wakes blocked waiters when the connection becomes unblocked.

## Dependencies And Interfaces
This file uses simplefs helpers, VFS inode/dentry APIs, FUSE global connection lists, and module filesystem registration. It is wired into the FUSE module init/exit path through `fuse_ctl_init()` and `fuse_ctl_cleanup()`.

## Concurrency And Safety
`fuse_mutex` protects the singleton superblock and connection pointer lookup/removal. `fc->bg_lock` protects background throttling fields. `READ_ONCE`/`WRITE_ONCE` are used for limit reads/writes where appropriate.

## Research Notes
Each control inode stores `fc` in `i_private`; removal clears this pointer so later file operations can return as if the connection disappeared. The returned dentries from creation are borrowed references valid while `fuse_mutex` is held.
