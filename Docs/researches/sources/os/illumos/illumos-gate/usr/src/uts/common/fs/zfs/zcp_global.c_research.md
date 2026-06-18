# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/zcp_global.c

## Role
Loads global errno constants into the ZFS Channel Program Lua environment.

## Main Logic
- Defines `zcp_errno_global_t` as a name-to-errno mapping.
- `errno_globals[]` includes common filesystem/system errnos such as `EPERM`, `ENOENT`, `EIO`, `ENOMEM`, `EACCES`, `EINVAL`, `ENOSPC`, `EROFS`, `ENOTSUP`, `EDQUOT`, and `ENAMETOOLONG`.
- `zcp_load_errno_globals()` iterates the table, pushes each errno as a Lua number, and sets it as a global.
- `zcp_load_globals()` currently delegates only to errno loading.

## Important Details
- The table terminates with `{NULL, 0}`.
- These globals let channel programs compare numeric errno returns from ZFS library calls without hard-coding platform values.
