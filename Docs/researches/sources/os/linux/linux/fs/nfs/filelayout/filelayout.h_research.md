# File Research: sources/os/linux/linux/fs/nfs/filelayout/filelayout.h

## Role

`filelayout.h` defines the internal data structures and helper declarations for the NFSv4.1 pNFS files layout driver.

## Constants And Types

The header caps supported geometry at:
- `NFS4_PNFS_MAX_STRIPE_CNT` = 4096 stripe indices,
- `NFS4_PNFS_MAX_MULTI_CNT` = 256 multipath list entries.

It defines `enum stripetype4` with `STRIPE_SPARSE` and `STRIPE_DENSE`.

## Core Structures

`struct nfs4_file_layout_dsaddr` stores decoded GETDEVICEINFO data: generic deviceid node, stripe count, stripe index array, number of data-server entries, and a flexible array of `struct nfs4_pnfs_ds *`.

`struct nfs4_filelayout_segment` extends `struct pnfs_layout_segment` with stripe type, commit-through-MDS flag, stripe unit, first stripe index, pattern offset, deviceid, decoded DS address pointer, filehandle count, and filehandle array.

`struct nfs4_filelayout` extends `struct pnfs_layout_hdr` with pNFS DS commit information.

## Helpers And External Interfaces

Inline helpers convert generic pNFS structures to filelayout-specific containers: `FILELAYOUT_FROM_HDR()`, `FILELAYOUT_LSEG()`, and `FILELAYOUT_DEVID_NODE()`.

The header declares geometry and DS selection helpers implemented in `filelayoutdev.c`, plus deviceid allocation/release helpers used by `filelayout.c`.

`filelayout_test_devid_invalid()` checks the generic invalid bit, while `filelayout_test_devid_unavailable()` also includes transient unavailable state.
