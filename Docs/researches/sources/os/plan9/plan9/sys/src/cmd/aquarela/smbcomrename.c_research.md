# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomrename.c

Server handler for `SMB_COM_RENAME`.

Key behavior:
- Parses old/new path strings and requires buffer format `0x04` for each.
- Prefixes service root, splits both paths into directory/name parts, and only allows same-directory rename.
- Calls `dirwstat` with new name.
- Returns ack or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses `smbpathsplit` and Plan 9 `dirwstat`.

Notable details:
- Cross-directory rename is rejected.
