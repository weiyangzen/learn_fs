# File Research: sources/os/linux/linux/fs/nfsd/flexfilelayoutxdr.h

Read completely: 50 lines.

Flex-file layout XDR data definitions and encoder declarations.

Key responsibilities:
- Defines flexfile flags for no layoutcommit, no I/O through MDS, and no read I/O.
- Defines fixed buffer lengths for flexfile netid and universal address strings.
- Defines `pnfs_ff_netaddr`, `pnfs_ff_device_addr`, and `pnfs_ff_layout`.
- Declares `nfsd4_ff_encode_getdeviceinfo` and `nfsd4_ff_encode_layoutget`.

Dependencies:
- Includes inet address length definitions and NFSv4 XDR layout types from `xdr4.h`.

Notable risks:
- Address buffers are fixed-size and rely on callers respecting `FF_NETID_LEN` and `FF_ADDR_LEN`.
