# File Research: sources/local-fs/xfsprogs/db/xfs_admin.sh

Shell wrapper implementing legacy `xfs_admin` behavior through `xfs_db`, `xfs_io`, and `xfs_repair`.

Key responsibilities:
- Parses admin options for lazycount, extflg, log2, label, feature upgrades, projid32bit, realtime device, UUID, and version.
- Selects online query/update paths with `xfs_io` for mounted filesystems when supported.
- Requires offline access for destructive or upgrade operations.
- Invokes `xfs_db -x` for expert metadata edits and `xfs_repair` for upgrade-style changes.

Important behavior:
- Uses `findmnt` to detect mounted XFS filesystems.
- Supports optional external log device argument.
- `-V` delegates version output to `xfs_db`.

Dependencies:
- External commands: `findmnt`, `xfs_db`, `xfs_io`, `xfs_repair`, and `expr`.

Notable risks:
- Builds command strings and executes them with `eval`; arguments with shell metacharacters rely on quoting discipline.
- `require_online` is defined but not meaningfully set by parsed options in this script.
