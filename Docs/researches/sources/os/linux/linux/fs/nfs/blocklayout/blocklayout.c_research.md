# File Research: sources/os/linux/linux/fs/nfs/blocklayout/blocklayout.c

Implements the NFSv4.1 pNFS block and SCSI layout driver.

Key responsibilities:
- Maps NFS page I/O to local block-device bios using pNFS extents.
- Handles parallel bio completion and final pNFS callbacks.
- Decodes layout extents from XDR.
- Verifies extent ordering/coverage constraints.
- Manages layout segment allocation/free and range return.
- Registers both block volume and SCSI layout driver types.
- Integrates with NFS pageio coalescing and layoutcommit.

Important components:
- `struct parallel_io`: refcounts multiple bios under one pNFS read/write operation.
- `do_add_page_to_bio()`: translates file sectors through extent/device maps and appends pages to bios.
- `bl_read_pagelist()`: reads pages from block devices or zero-fills holes.
- `bl_write_pagelist()`: writes full pages to block devices.
- `verify_extent()`: validates READ/RW extent sequences.
- `bl_alloc_lseg()`: decodes XDR extent list into the extent tree.
- `bl_pg_init_read/write()` and `bl_pg_test_read/write()`: enforce alignment and initialize pNFS pageio.
- `blocklayout_type` and `scsilayout_type`: registered pNFS layout drivers.

Important behavior:
- Holes are detected from extent state and zero-filled without device I/O.
- Device mapping failures mark device IDs unavailable, set layout failure, and trigger fallback.
- Bio errors set `pnfs_error`, mark layout segment failed, and mark devices unavailable.
- Writes mark extents written and update layoutcommit state after successful I/O.
- Direct I/O requires sector/page alignment depending on read/write path; misaligned requests fall back to metadata server.
- Server `pnfs_blksize` must be nonzero and no larger than `PAGE_SIZE`.

Dependencies:
- NFS pNFS core APIs.
- Block device/bio APIs.
- Extent tree helpers from `extent_tree.c`.
- Device registration helpers from `dev.c`.
- rpc_pipefs helpers for block device resolution.

Module registration:
- Registers aliases `nfs-layouttype4-3` and `nfs-layouttype4-5`.
- Init creates pipefs integration and registers both layout types.
- Exit unregisters both layout types and cleans pipefs.
