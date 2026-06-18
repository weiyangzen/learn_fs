# File Research: sources/os/illumos/illumos-gate/usr/src/cmd/zfs/zfs_projectutil.h

Private header shared by `zfs_main.c` and `zfs_project.c` for `zfs project` control flow.

Exports:
- `zfs_project_ops_t` operation enum:
  - `ZFS_PROJECT_OP_DEFAULT`
  - `ZFS_PROJECT_OP_LIST`
  - `ZFS_PROJECT_OP_CHECK`
  - `ZFS_PROJECT_OP_CLEAR`
  - `ZFS_PROJECT_OP_SET`
- `zfs_project_control_t`, carrying parsed command flags and expected project ID.
- `zfs_project_handle(const char *name, zfs_project_control_t *zpc)`.

Control fields:
- `zpc_expected_projid`: explicit or discovered project ID.
- `zpc_op`: selected operation.
- `zpc_dironly`: operate on the directory itself rather than children.
- `zpc_ignore_noent`: suppress races for disappeared child paths.
- `zpc_keep_projid`: clear inherit flag without resetting project ID.
- `zpc_newline`: select newline or NUL output for check mode.
- `zpc_recursive`: recurse into subdirectories.
- `zpc_set_flag`: set the project inherit flag during set mode.

Integration role:
- `zfs_main.c` parses CLI options into this structure.
- `zfs_project.c` consumes it while validating targets, traversing directories, and issuing project xattr ioctls.

Risk notes:
- The meaning of some fields is operation-specific; CLI validation in `zfs_do_project()` prevents unsupported combinations before this structure reaches `zfs_project.c`.
- `zpc_ignore_noent` is mutable traversal state, not just a parsed option.
