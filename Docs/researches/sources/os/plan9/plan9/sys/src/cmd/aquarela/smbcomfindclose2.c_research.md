# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomfindclose2.c

Server handler for `SMB_COM_FIND_CLOSE2`.

Key behavior:
- Requires one parameter word containing search id.
- Calls `smbsearchclosebyid`.
- Returns an SMB ack.

Interactions:
- Search implementation is elsewhere; this file just dispatches close-by-id.

Notable details:
- Does not error if the search id is absent.
