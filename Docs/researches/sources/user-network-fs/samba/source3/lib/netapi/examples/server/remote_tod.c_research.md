# sources/user-network-fs/samba/source3/lib/netapi/examples/server/remote_tod.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/server/remote_tod.c

Purpose: Demonstrates querying remote server time with `NetRemoteTOD()`.

Important APIs/types/functions: Uses `TIME_OF_DAY_INFO` and prints year/month/day/hour/minute/second fields.

Control flow: Parses hostname, calls `NetRemoteTOD()`, prints the returned timestamp on success, frees the result buffer, and cleans up.

State and persistence behavior: Read-only server query with no local persistence.

Dependencies and integration points: Server administration example using standard libnetapi setup/teardown.

Risks: Displays server-provided fields without timezone explanation. Requires reachable remote service.

Test signals: Compare output against server clock within acceptable skew and verify error path for unreachable host.
