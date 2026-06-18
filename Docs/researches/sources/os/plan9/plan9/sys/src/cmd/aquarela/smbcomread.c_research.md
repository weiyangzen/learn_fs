# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbcomread.c

Server handler for `SMB_COM_READ_ANDX`.

Key behavior:
- Supports 32-bit and 64-bit offsets via word count 10 or 12.
- Validates tree id, fid, and `ioallowed`.
- Builds an AndX response with data offset/count fixups.
- Reads at most requested max count or available response buffer space from the file descriptor.
- Chains to next command when requested.

Interactions:
- Uses `seek` plus `readn` on Plan 9 fd.
- Relies on `smbbufferwritelimit` to cap payload to SMB max transfer size.

Notable details:
- Returns `ERRbadaccess` for directory fids or read errors.
