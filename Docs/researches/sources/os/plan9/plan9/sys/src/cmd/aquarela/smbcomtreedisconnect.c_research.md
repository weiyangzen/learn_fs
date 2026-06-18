# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomtreedisconnect.c

Server handler for `SMB_COM_TREE_DISCONNECT`.

Key behavior:
- Requires zero word count.
- Disconnects the tree by request tid.
- Returns ack.

Interactions:
- Calls `smbtreedisconnectbyid`, implemented outside this file.

Notable details:
- Does not report an error for absent tid in this wrapper.
