# File Research: sources/os/linux/linux/fs/xfs/xfs_globals.c

Defines global tunables and runtime defaults for XFS.

Key contents:
- `xfs_params` exposes min/default/max ranges for panic mask, error level, sync daemon timer, stats clear, inherited inode flags, rotor step, filestream timer, and blockgc timer. Most timers are centiseconds except `blockgc_timer`, which is seconds.
- `xfs_globals` sets defaults for log recovery delay, mount delay, assert behavior, debug-only parallel work threads and logged-attribute replay flag, and btree bulk-load slack for leaf/node blocks.

This file centralizes tunable defaults used even when sysctl support is disabled.
