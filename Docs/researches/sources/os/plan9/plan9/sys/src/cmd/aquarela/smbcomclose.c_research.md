# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomclose.c

Server handler for `SMB_COM_CLOSE`.

Key behavior:
- Requires word count 3.
- Validates tree id and fid.
- Calls `smbfileclose`, which removes the fid map entry, releases shared-file state, closes fd, and frees the file object.
- Returns an SMB ack.

Interactions:
- Uses `smbidmap`, `smbfile.c`, and `smbbufferputack`.

Notable details:
- Ignores close time fields in the request.
