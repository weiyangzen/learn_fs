# File Research: sources/local-fs/xfsprogs/db/xfs_ncheck.sh

Shell wrapper for legacy `xfs_ncheck` functionality via `xfs_db`.

Key responsibilities:
- Parses inode filters, summary/verbose options, force, log device, and version.
- Runs `xfs_db` readonly with `blockget -ns` followed by `ncheck`.

Important behavior:
- Requires exactly one filesystem/device operand.
- `-V` delegates version output to `xfs_db`.

Dependencies:
- External `xfs_db`.

Notable risks:
- Includes `b:` in the `getopts` string but has no `b)` case.
- Assembles command strings with unquoted shell expansions.
