# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.c

## Summary
XDR encoders for NFSD pNFS flex-file layout and device info.

## Main APIs
- `nfsd4_ff_encode_layoutget()`.
- `nfsd4_ff_encode_getdeviceinfo()`.

## Behavior
Layoutget encoding emits a single mirror, single data server, deviceid, stateid, single filehandle, stringified uid/gid, flex-file flags, and zero stats hint. Deviceinfo encoding emits one netaddr and one NFSv3 version record with advertised read/write sizes. If `gd_maxcount` is zero, it follows RFC guidance by returning a zero-length result.

## Risks
Length calculation is manual and must stay aligned with the XDR fields. UID/GID are formatted in the initial user namespace rather than through the ordinary NFSv4 idmapper.
