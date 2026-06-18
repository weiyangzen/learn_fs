<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.h -->
# sources/user-network-fs/samba/source3/utils/conn_tdb.h

## Purpose
`conn_tdb.h` defines the connection summary record and traversal API shared by smbd and status utilities.

## Important APIs, types, and functions
- `struct connections_data` contains server id, tree id, session id, uid/gid, service name, client address/machine, start time, SMB encryption/signing fields, dialect, and authentication flag.
- `connections_forall_read()` iterates active connection records and invokes a callback with optional private data.

## Control flow
The header does not implement control flow; it documents the callback shape consumed by readers of active connection state.

## State and persistence behavior
`connections_data` is a snapshot representation. It is not the persistent database format; current implementations synthesize it from live SMB session/tcon global state.

## Dependencies and integration points
It includes Samba source3 base headers for `server_id`, `fstring`, `NTTIME`, and related scalar types. Consumers include server status/reporting code and the implementation in `conn_tdb.c`.

## Risks and edge cases
- The structure is shared across utilities, so field additions can affect ABI expectations inside the tree.
- `uid_t` and `gid_t` may use `-1` sentinel values in practice even though their signedness is platform-dependent.
- Crypto fields are compact numeric representations that callers must format with the right dialect/signing/cipher lookup.

## Test signals
Compile coverage plus status utilities displaying all fields correctly are the main validation signals.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source3/utils/conn_tdb.h -->
