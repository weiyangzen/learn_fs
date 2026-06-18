# File Research: sources/local-fs/ocfs2-tools/extras/watch-hb.sh

Read coverage: complete file read, 40 lines.

Purpose: watches OCFS2 heartbeat data through `debugfs.ocfs2`.

Behavior:
- Accepts either `-r <region>` or `-d <device>`.
- For a region, reads `$region/dev` and tries to read a slot-byte attribute; for direct device mode, uses 512-byte slots.
- Runs `watch -n 3 -d` around a pipeline that cats `//heartbeat` through `debugfs.ocfs2 -n`, formats it with `od`, and filters slot-aligned rows with `awk`.

Dependencies: `watch`, `debugfs.ocfs2`, `od`, `awk`, shell `/sys`-style heartbeat region files.

Risk notes:
- Read-only display helper.
- The region branch references `$attr` without setting it in this script, so region mode likely depends on external environment or is broken.
- Uses `eval` unnecessarily for simple assignments.
