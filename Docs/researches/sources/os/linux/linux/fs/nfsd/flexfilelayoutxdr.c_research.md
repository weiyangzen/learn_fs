# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.c

Read completely: 124 lines.

XDR encoder for the NFSD pNFS flex-file layout and device-address payloads.

Key responsibilities:
- Encodes layoutget content as one stripe unit, one mirror, one data server, one deviceid, one stateid, one filehandle, stringified UID/GID, flexfile flags, and no stats-collection hint.
- Computes encoded lengths for nested mirror/data-server/filehandle structures before reserving XDR space.
- Encodes getdeviceinfo as either an empty result when `gd_maxcount` is zero, or one netaddr and one NFS version tuple with rsize/wsize/tightly-coupled fields.

Dependencies:
- Uses `xdr_stream`, `xdr_reserve_space`, opaque string encoders, `svcxdr_encode_deviceid4`, and init user namespace id conversion.

Notable risks:
- Length calculation is manual and must stay aligned with RFC layout field encoding.
- UID/GID buffers are fixed at 11 bytes, matching decimal u32 text plus terminator expectations.
