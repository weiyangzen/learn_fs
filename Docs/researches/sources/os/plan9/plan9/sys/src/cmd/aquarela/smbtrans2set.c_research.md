# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/smbtrans2set.c

Implements server-side TRANS2 set-file and set-path information operations.

Key points:
- `smbtrans2setfileinformation` handles allocation/EOF truncation, basic timestamps/attributes, and delete-on-close disposition.
- `smbtrans2setpathinformation` handles `SMB_INFO_STANDARD`, translating DOS packed dates/times and attributes to Plan 9 `Dir` updates.
- Uses `dirfwstat` for FID-based updates and `dirwstat` for path-based updates.

Dependencies:
- Uses tree and FID maps, SMB transaction input buffers, Plan 9 `Dir`, `smbtruncatefile`, and DOS attribute conversion.

Notable behavior:
- Unsupported info levels return `ERRunknownlevel`.
- Size updates in path standard info are applied when nonzero; commented code shows uncertainty around zero-size handling.
