# File Research: sources/os/linux/linux-stable/fs/nfs/filelayout/filelayout.h

## Role

`filelayout.h` defines the pNFS file-layout driver's private data structures, layout type constants, accessor helpers, and cross-file function declarations shared by `filelayout.c` and `filelayoutdev.c`.

## Constants and layout types

- `NFS4_PNFS_MAX_STRIPE_CNT` is `4096`, the supported maximum number of stripe indices.
- `NFS4_PNFS_MAX_MULTI_CNT` is `256`, chosen because stripe indices are stored as `u8`.
- `enum stripetype4` defines `STRIPE_SPARSE = 1` and `STRIPE_DENSE = 2`.

## Data structures

`struct nfs4_file_layout_dsaddr` embeds the generic `nfs4_deviceid_node`, stores stripe count, an array of `u8` stripe indices, the number of data-server multipath entries, and a flexible array of `struct nfs4_pnfs_ds *`.

`struct nfs4_filelayout_segment` embeds `struct pnfs_layout_segment` and stores stripe type, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, deviceid, resolved data-server address, number of filehandles, and the decoded filehandle array.

`struct nfs4_filelayout` embeds the generic layout header and stores filelayout pNFS data-server commit info.

## Helper API

Inline helpers convert generic pNFS headers/segments to filelayout types: `FILELAYOUT_FROM_HDR()`, `FILELAYOUT_LSEG()`, and `FILELAYOUT_DEVID_NODE()`. `filelayout_test_devid_invalid()` checks the generic `NFS_DEVICEID_INVALID` flag.

The header declares deviceid availability checks, data-server filehandle selection, stripe/data-server index calculations, data-server preparation, deviceid allocation/free/put helpers, and deviceid-node allocation for the layoutdriver.

## Integration

This header is intentionally narrow: policy and I/O logic live in `filelayout.c`, while XDR GETDEVICEINFO decoding, data-server connection, and stripe-index helpers live in `filelayoutdev.c`.
