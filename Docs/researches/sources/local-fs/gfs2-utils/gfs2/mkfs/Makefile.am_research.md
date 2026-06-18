# File Research: sources/local-fs/gfs2-utils/gfs2/mkfs/Makefile.am

Automake build definition for mkfs/grow/jadd tools.

Targets:
- `mkfs.gfs2`
- `gfs2_jadd`
- `gfs2_grow`

Behavior:
- Defines shared CPP flags with `_GNU_SOURCE`.
- Lists private headers.
- Links all tools against `gfs2/libgfs2/libgfs2.la`.
- Adds blkid, uuid, and intl libraries where needed.
- Includes `checks.am` when Check framework is available.

Risk notes:
- Build flags and libraries differ per binary; changing shared code may require matching link dependencies.
- Unit test targets include production source files with `-DUNITTESTS`.
