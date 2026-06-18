# File Research: sources/local-fs/xfsprogs/db/agi.c

Defines the `agi` command and allocation group inode header field layout. `agi_flds` exposes AGI identity/accounting fields, inode btree roots/levels, free inode counters, `newino`, `dirino`, unlinked inode buckets, uuid/crc/lsn, and finobt accounting. Root fields point to `TYP_INOBT` and `TYP_FINOBT`; selected inode references point to `TYP_INODE`.

The command validates an optional AG number, defaults to AG 0 if needed, and sets the current cursor to `XFS_AGI_DADDR` for one sector. `agi_size` returns sector size in bits. This file is read-only interactive navigation metadata, not repair logic.
