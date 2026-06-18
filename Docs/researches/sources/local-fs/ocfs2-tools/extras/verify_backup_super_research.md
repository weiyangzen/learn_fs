# File Research: sources/local-fs/ocfs2-tools/extras/verify_backup_super

Read coverage: complete file read, 159 lines.

Purpose: shell helper that finds filesystem objects occupying clusters reserved for OCFS2 backup superblocks, useful before enabling backup superblocks retroactively.

Behavior:
- Requires `debugfs.ocfs2`, `awk`, `seq`, `tee`, and `date`.
- Reads block-size bits, cluster-size bits, and cluster count from `debugfs.ocfs2 -R stats`.
- Verifies `debugfs.ocfs2` version is at least 1.2.3.
- Exits early if the BackupSuper compat feature is already enabled.
- Converts fixed backup-super offsets from 512-byte sectors to filesystem blocks.
- Runs `debugfs.ocfs2 -R "icheck ..."` to find inodes using those blocks.
- If any are found, runs `debugfs.ocfs2 -R "findpath ..."` to map inodes to names.

Dependencies: external OCFS2 debugfs command and shell arithmetic.

Risk notes:
- Read-only script.
- Uses `/tmp/__${timestamp}__` without cleanup or collision hardening.
- The `get_sizes()` empty checks use `-a` string tests in a suspicious way, but intent is to reject missing stats.
