# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/zfs/sys/zfs_stat.h

Defines a small ZPL statistics structure exported through ioctl paths.

Key elements:
- `zfs_stat_t` contains generation, mode, link count, and ctime.
- Declares `zfs_obj_to_stats()` to convert an object number into stats and optional path/name buffer data.

Main dependencies and interactions:
- Used by `zfs_ioctl.h` inside `zfs_cmd_t`.
- Current documented consumer is `zfs diff`.

Implementation notes:
- This is a deliberately limited stat ABI, not a full vnode/stat replacement.
