# File Research: sources/os/linux/linux-stable/fs/xfs/xfs_message.c

## Purpose
Provides XFS-specific kernel logging, assertion reporting, panic-tag alert conversion, hex dumps, buffer I/O alert rate limiting, and one-time experimental feature warnings.

## Main APIs
- `xfs_printk_level` formats XFS messages with mount/superblock identity and optionally emits stack traces for high error verbosity.
- `_xfs_alert_tag` emits alert messages and converts selected panic-mask tags into `BUG`.
- `asswarn` and `assfail` implement warning/fatal assertion reporting.
- `xfs_hex_dump` prints alert-level hex dumps.
- `xfs_buf_alert_ratelimited` emits per-buffer-target rate-limited alerts.
- `xfs_warn_experimental` warns once per mount for shrink, logged xattrs, and zoned realtime features.

## Key Behavior
Messages include `XFS (<s_id>):` when a mounted superblock is available, otherwise plain `XFS:`. Assertions use `WARN_ON` unless configured to BUG on assertion failure. Experimental warnings are gated by mount opstate bits so each feature warning is emitted once.
