# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_project.c

This file implements the file-tree side of `zfs project`, using ZFS project quota ioctls to list, check, clear, or set project IDs and the project-inherit flag on files and directories.

Main API:
- `zfs_project_handle(name, zpc)`: validates the top-level target, fills an expected project ID when needed, handles the target itself, and optionally walks directory children.

Operation behavior:
- `ZFS_PROJECT_OP_LIST`: prints project ID, project inherit flag state, and path.
- `ZFS_PROJECT_OP_CHECK`: reports paths whose project ID or inherit flag does not match the expected state; `-0` mode prints NUL-terminated path names.
- `ZFS_PROJECT_OP_CLEAR`: clears `ZFS_PROJINHERIT_FL` and, unless `keep_projid` is set, resets the project ID to `ZFS_DEFAULT_PROJID`.
- `ZFS_PROJECT_OP_SET`: sets the expected project ID and optionally sets `ZFS_PROJINHERIT_FL`.

Validation:
- Top-level targets must `stat()` successfully and must be regular files or directories.
- `-d` and `-r` are rejected for non-directory targets.
- If set/check mode has no explicit expected project ID, the top-level target's current project ID is loaded through `ZFS_IOC_FSGETXATTR`.

Traversal:
- Uses illumos `list_t` as a queue of directory names for recursive traversal.
- `zfs_project_handle_dir()` opens a directory, handles each child with `zfs_project_handle_one()`, and enqueues subdirectories when recursive mode is active.
- After the top-level item is processed, `zpc_ignore_noent` is enabled so disappearing non-top children are ignored as directory traversal races.
- `zpc_dironly` prevents child traversal after the top directory itself is handled.

Ioctl behavior:
- Opens each file/directory read-only with `O_NOCTTY`.
- Reads `zfsxattr_t` via `ZFS_IOC_FSGETXATTR`.
- Writes modified `zfsxattr_t` via `ZFS_IOC_FSSETXATTR` for set/clear operations.

State and ownership:
- Queue entries are allocated with a flexible `zpi_name` tail and freed as they are removed.
- File descriptors are closed on every operation path after opening.

Risk notes:
- Path construction uses fixed `PATH_MAX` buffers; long names produce `ENAMETOOLONG`.
- Recursive traversal is race-tolerant for removed children but not a snapshot of the tree.
- The code uses `stat64()` after `readdir()` to identify subdirectories, so symlink and rename behavior follows normal `stat` semantics.
- Set/check default expected ID comes from the top-level target, which is important for recursive project-tree normalization.
