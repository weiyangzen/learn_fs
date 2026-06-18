# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomdeletedir.c

Server handler for `SMB_COM_DELETE_DIRECTORY`.

Key behavior:
- Parses a path, resolves tree id, prefixes service root, and calls `remove`.
- Returns ack on success or `ERRDOS/ERRnoaccess`.

Interactions:
- Uses same tree/path pattern as create-directory handler.

Notable details:
- Does not distinguish nonexistent path, nonempty directory, and permission failures.
