# File Research: sources/teaching/minix/minix/servers/vfs/gcov.c

Coverage-data retrieval support for system services.

Key function:
- `do_gcov_flush`

Behavior:
- Superuser-only.
- Copies a service label and resolves it through DS.
- Rejects `init` as a target.
- Grants the target service write access to the caller’s supplied buffer.
- If target is VFS, calls `gcov_flush` directly.
- Otherwise sends `COMMON_REQ_GCOV_DATA` to the target service.
- Revokes the grant before returning.

Operational note:
- The file comments warn that the call is sensitive and can deadlock the system because it calls into arbitrary target services.
