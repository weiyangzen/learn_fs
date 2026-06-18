# File Research: sources/virtualization/libnbd/lib/protocol.c

Small protocol mapping helper module.

Key functions:
- `nbd_internal_errno_of_nbd_error`: maps NBD wire error codes to local errno values.
- `nbd_internal_name_of_nbd_cmd`: maps command type codes to readable names.

Interactions:
- Completion paths in `aio.c` use command names for errors.
- Reply-handling state code can use errno mapping for server replies.

Research notes:
- Unknown NBD errors map to `EINVAL`.
- Comment notes similar command-name mapping is generated in nbdkit and could be unified.
