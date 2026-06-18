# File Research: sources/virtualization/libblockdev/src/plugins/fs/xfs.c

Implements XFS support through xfsprogs utilities.

Key entry points:
- `bd_fs_xfs_is_tech_avail()` checks XFS utility dependencies.
- `bd_fs_xfs_mkfs()` runs `mkfs.xfs`.
- `bd_fs_xfs_check()` runs `xfs_repair -n`.
- `bd_fs_xfs_repair()` runs `xfs_repair`.
- `bd_fs_xfs_set_label()` and `_set_uuid()` use `xfs_admin`.
- `bd_fs_xfs_get_info()` uses `xfs_spaceman info` for mounted filesystems or `xfs_db -r -c info` for unmounted devices.
- `bd_fs_xfs_resize()` runs `xfs_growfs`.

Core mechanics:
- Dependencies are `mkfs.xfs`, `xfs_db`, `xfs_repair`, `xfs_admin`, and `xfs_growfs`.
- Mkfs options map label, metadata UUID, dry run, no-discard, force, and extra args.
- Check treats a nonzero `xfs_repair -n` exit as “filesystem not clean” rather than a command error when the utility itself ran.
- Empty labels are passed to `xfs_admin -L --`.
- A `NULL` UUID maps to `xfs_admin -U generate`.
- Info first obtains UUID/label via common probing, then parses block size and block count from an XFS `data` line.
- Mounted filesystems use `xfs_spaceman` to avoid stale `xfs_db` data; unmounted filesystems use `xfs_db -r` to avoid write-side effects.
- Resize accepts size in filesystem blocks for `xfs_growfs -D`.

Important invariants:
- XFS labels are at most 12 characters and cannot contain spaces.
- XFS resize is grow-only and requires a mounted filesystem; generic code handles device-to-mountpoint conversion.
- UUID validation uses common UUID validation, with special tool-level values documented for set-uuid.

Filesystem/block relevance:
- Provides XFS creation, check/repair, metadata query, label/UUID management, and online grow support.

Notable risks:
- Info parsing depends on the exact `data = bsize=... blocks=...` output shape.
- `bd_fs_xfs_check()` comments note that mounted RW filesystems are always reported not clean.
- Capability metadata lists `xfs_db` for check, while implementation uses `xfs_repair -n`.
