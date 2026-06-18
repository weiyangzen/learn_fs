# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtree.c

Manages SMB tree connections within a session.

Key points:
- `smbtreeconnect` creates the session TID map if needed, allocates a tree, inserts it, references the service, and logs the new TID.
- `smbtreedisconnect` logs, releases the service reference, closes all searches and files attached to the tree, removes the TID, and frees the tree.
- `smbtreedisconnectbyid` finds by TID then delegates.

Dependencies:
- Uses `SmbSession`, `SmbTree`, service reference management, SID/FID/TID maps, and search/file close helpers.

Notable behavior:
- Disconnect cleanup is map-wide and filters entries by owning tree.
