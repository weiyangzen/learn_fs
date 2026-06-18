# File Research: sources/local-fs/squashfs-tools/squashfs-tools/fnmatch_compat.h

Compatibility header for pattern matching.

Behavior:
- Includes `<fnmatch.h>`.
- Defines `FNM_EXTMATCH` to `0` if the platform does not provide it.

Key role: allows action-language pattern matching to request extended match syntax where available while remaining buildable on platforms without that flag.
