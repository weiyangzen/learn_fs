# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomcreatedir.c

Server handler for `SMB_COM_CREATE_DIRECTORY`.

Key behavior:
- Requires zero parameter words and buffer format `0x04`.
- Reads an SMB path, resolves the tree id, prefixes the service path, and calls Plan 9 `create` with `DMDIR | 0775`.
- Returns ack or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses `smbbuffergetstring` for path conversion and `smbidmapfind` for tree lookup.

Notable details:
- Logs the requested path and failure reason.
