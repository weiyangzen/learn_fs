# File Research: sources/os/plan9/9front/sys/src/cmd/cifs/transnt.c

Implements the SMB `SMB_COM_NT_TRANSACT` subset needed by this CIFS client: querying owner/group security descriptors.

Internal helpers construct NT transaction headers, fill parameter/data counts and offsets, dispatch via `cifsrpc`, and position returned cursors.

`TNTquerysecurity` sends `NT_TRANSACT_QUERY_SECURITY_DESC` for owner and group security information on an open file handle. It parses the returned security descriptor offsets and formats Windows SIDs as strings like `S-1-5-...`.

The function is consumed by `sid2name.c` to update Plan 9 `Dir` uid/gid fields for remote files.

Scope is intentionally narrow: no DACL/SACL parsing, no security descriptor mutation, and no generalized NT transaction framework beyond the single query operation.
