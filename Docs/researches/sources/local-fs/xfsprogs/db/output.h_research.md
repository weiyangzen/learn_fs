# File Research: sources/local-fs/xfsprogs/db/output.h

## Purpose
Declares xfs_db output and logging interfaces.

## Interfaces
- `dbprefix` controls device-name prefixing.
- `dbprintf()` is the main user-facing formatter.
- `logprintf()` writes to the active log.
- `output_init()` registers output-related commands.
