# sources/user-network-fs/samba/source3/lib/netapi/examples/server/server_getinfo.c

## sources/user-network-fs/samba/source3/lib/netapi/examples/server/server_getinfo.c

Purpose: Demonstrates querying server metadata through `NetServerGetInfo()`.

Important APIs/types/functions: Handles levels 100, 101, 102, and 1005; recognizes but does not print full details for 402, 403, 502, and 503.

Control flow: Parses hostname and level, calls the API, switches on level to print platform/name/version/type/comment/session fields or comment-only data, frees the buffer, and exits.

State and persistence behavior: Read-only server metadata query.

Dependencies and integration points: Used by GUI initialization and server administration examples.

Risks: Some supported levels are placeholders. Fields like passwords/userpath are printed directly where structures expose them.

Test signals: Query common levels against Samba and Windows servers and validate unsupported-level behavior.
