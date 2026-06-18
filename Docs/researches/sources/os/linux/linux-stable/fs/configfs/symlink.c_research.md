# File Research: sources/os/linux/linux-stable/fs/configfs/symlink.c

This file implements configfs symlink creation and unlink semantics.

Key responsibilities:
- Defines `configfs_symlink_mutex`.
- Resolves symlink targets to configfs items at syscall time.
- Builds relative symlink bodies from the link parent to the target item.
- Calls client `allow_link()` and `drop_link()` callbacks.
- Updates target dirent link counts to block unsafe removal.

Important control flow:
- `configfs_symlink()`:
  - Rejects not-ready parent directories.
  - Requires the parent item type to provide `allow_link`.
  - Temporarily unlocks the parent inode to resolve `symname` via `kern_path()`, then relocks and revalidates the dentry.
  - Calls `allow_link()`, then creates the link under `configfs_symlink_mutex`.
- `create_link()`:
  - Ensures target dirent is ready and not dropping.
  - Increments target `s_links`.
  - Computes a relative target path and calls `configfs_create_link()`.
  - Rolls back link count and references on failure.
- `configfs_unlink()` removes the symlink dirent, drops the dentry, invokes `drop_link()` before decrementing target link count, and releases references.

Dependencies:
- Uses directory/inode helpers from `dir.c` and `inode.c`.
- Depends on public configfs item callbacks.

Risks and invariants:
- Configfs symlinks are unusual: the target is resolved at symlink creation time and pins/removal-blocks a config item.
- The file contains explicit warnings that these semantics differ from normal symlink behavior and require careful locking.
- Target paths are bounded by `PATH_MAX`.
- Symlink targets must be on the same configfs superblock.
