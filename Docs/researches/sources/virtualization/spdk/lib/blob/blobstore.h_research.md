# File Research: sources/virtualization/spdk/lib/blob/blobstore.h

Private blobstore implementation header. It defines the in-memory shape of blob metadata, blobstore state, per-channel request queues, open blob trees, snapshot clone lists, external snapshot tracking, and the request operation types used by blob I/O.

Key in-memory structures:
- `spdk_blob_mut_data` stores mutable persistent blob layout: cluster LBA array, metadata page chain, extent-page table, and allocation counts.
- `spdk_blob` keeps clean/active copies of mutable data, xattrs, flags, parent/snapshot state, lock/freeze state, extent-table parsing state, and pending persist queues.
- `spdk_blob_store` tracks metadata region geometry, backing device, allocation bitmaps, open blobs, snapshots, super blob id, blobstore type, unload state, and external snapshot unload coordination.
- `spdk_bs_channel` owns request-set memory, queued I/O, cluster allocation/free queues, temporary metadata pages, and external snapshot channels.

The on-disk portion defines blobstore metadata page, superblock, mask, xattr, flag, extent RLE, extent table, and extent page descriptor formats. It also defines blob feature/compatibility flag masks, descriptor type constants, metadata page size assertions, and extent-page sizing.

Inline helpers convert between bytes, LBAs, metadata pages, clusters, I/O units, blob ids, and extent-table slots. Blob ids deliberately set a high bit above the low 32-bit metadata page index to catch code that confuses page indices with blob ids. `bs_blob_io_unit_to_lba()` maps blob-relative I/O units through the active cluster table and returns zero for unallocated thin-provisioned clusters.
