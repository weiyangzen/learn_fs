# File Research: sources/os/linux/linux-stable/fs/nfsd/flexfilelayoutxdr.h

## Summary
Definitions for NFSD flex-file layout encoding.

## Contents
Defines flex-file flags, fixed netid/address buffer sizes, `struct pnfs_ff_netaddr`, `struct pnfs_ff_device_addr`, and `struct pnfs_ff_layout`. Declares layoutget and getdeviceinfo encoder functions.

## Important Details
`pnfs_ff_layout` stores layout flags, uid/gid, deviceid, stateid, and an embedded NFS filehandle. Device addresses carry netid, universal address, NFS version/minor version, rsize/wsize, and tight-coupling flag.

## Risks
The fixed address buffer depends on `INET6_ADDRSTRLEN + 8` being enough for the universal address plus encoded port suffix.
