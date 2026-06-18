# File Research: sources/local-fs/squashfs-tools/squashfs-tools/uid_gid.c

This file parses user/group arguments into numeric 32-bit ids for command-line options.

Key functions:
- `get_uid_from_arg(char *arg, unsigned int *uid)`.
- `get_gid_from_arg(char *arg, unsigned int *gid)`.

Behavior:
- First attempts decimal numeric parsing via `strtoll`.
- If the whole argument is numeric, validates range `0..2^32-1`.
- If nonnumeric, resolves username with `getpwnam` or group name with `getgrnam`.
- Retries name lookup on `EINTR`.

Return values:
- `0`: success.
- `-1`: name lookup failed or nonnumeric name not found.
- `-2`: numeric id was outside the supported unsigned 32-bit range.

Important details:
- The numeric parser does not reset/check `errno` for `strtoll` overflow; range validation catches many, but not all, overflow-reporting subtleties.
- Returned ids are stored in `unsigned int`, matching Squashfs id-table storage expectations.
