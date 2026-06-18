# File Research: sources/local-fs/xfsprogs/db/timelimit.c

Implements the `xfs_db` `timelimit` command.

Key responsibilities:
- Prints supported inode timestamp, quota timer, and quota grace-period limits.
- Supports classic and bigtime limits.
- Supports raw, pretty `ctime`, and compact single-line output.
- Auto-selects classic vs bigtime based on filesystem feature flags.

Important behavior:
- Grace periods are always printed as integer values, even in pretty mode.
- `--classic`, `--bigtime`, `--pretty`, and `--compact` are parsed manually.

Dependencies:
- Uses XFS time conversion constants/helpers and `xfs_has_bigtime(mp)`.

Notable risks:
- Output label for grace maximum is `dqgrace.min` instead of `dqgrace.max`, likely a typo in `show_limits`.
