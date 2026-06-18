# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbclientopen.c

Client-side implementation of `SMB_COM_OPEN`.

Key function:
- `smbclientopen` builds an open request using the client prototype header, share tree id, mode, and path; sends it through NBSS; reads the response; validates header; and returns fid, attributes, mtime, size, and access-allowed fields.

Interactions:
- Called by `cifscmd.c`.
- Uses `smbbuffer`, `smbcommon`, and `nbss` client transport.

Notable details:
- The assignment `*sizep = smbnhgets(pdata); pdata += 4;` reads a 16-bit value while advancing four bytes, which looks suspicious for a 32-bit size field.
