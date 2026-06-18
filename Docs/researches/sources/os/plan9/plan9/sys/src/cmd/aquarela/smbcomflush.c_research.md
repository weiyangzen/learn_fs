# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomflush.c

Server handler for `SMB_COM_FLUSH`.

Key behavior:
- Validates tree id and fid.
- Builds an all-`0xff` `Dir` with nil name/user fields and calls `dirfwstat` on the file descriptor.
- Returns ack.

Interactions:
- Uses Plan 9 directory metadata update as a flush-ish operation.

Notable details:
- Ignores `dirfwstat` return value.
