# File Research: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.h

This header declares the UID/GID parsing helpers.

Public interface:
- `get_uid_from_arg(char *arg, unsigned int *uid)`.
- `get_gid_from_arg(char *arg, unsigned int *gid)`.

Expected semantics:
- Numeric strings resolve directly after range checking.
- Nonnumeric strings resolve through system passwd/group databases.
- Callers should distinguish `-1` not found from `-2` out of range for diagnostics.
