# File Research: sources/virtualization/qemu/block/vdi.c

`vdi.c` implements QEMU's VirtualBox VDI image format driver. It supports probing, opening, checking, reading, writing, creating dynamic/static images, block status, zero-init reporting, and migration blocking. Snapshots, backing files, shrinking, and deallocation are explicitly absent or TODO.

The on-disk format is represented by `VdiHeader`, a packed 512-byte structure with signature/version/type, block map/data offsets, disk geometry, sector size, disk size, block size, block counts, and UUIDs. `BDRVVdiState` stores the little-endian block map in memory, block size, first block-map sector, host-endian header, a coroutine rwlock for bmap access, and a migration blocker. Constants define VDI signature/version, dynamic/static image types, default 1 MiB clusters, unallocated/discarded block markers, maximum block-map entries, and maximum supported disk size.

Endian helpers convert the header between disk little-endian and host order, including UUID byte swapping. `vdi_header_print()` is debug-only logging. `vdi_probe()` returns high confidence when the header signature matches. `vdi_open()` opens the `"file"` child, reads and validates the header, rounds odd disk sizes up to 512 bytes for compatibility, rejects unsupported signatures, versions, unaligned map/data offsets, non-512 sector sizes, non-default block sizes, impossible disk sizes, non-null link/parent UUIDs, and excessive block counts. It sets `bs->total_sectors`, allocates an aligned in-memory block map, reads it, installs a live-migration blocker, and initializes the bmap lock.

`vdi_co_check()` validates the block map and allocated count. It rejects repair mode, builds a temporary map to detect duplicate physical block indices, reports entries outside range, and compares counted allocated blocks with `header.blocks_allocated`. `vdi_co_get_info()` reports cluster size. `vdi_make_empty()` is a stub returning success as required by block-layer expectations.

Block status maps one cluster at a time. `vdi_co_block_status()` looks up the block-map entry, returns `BDRV_BLOCK_ZERO` for unallocated/discarded entries, otherwise maps to `offset_data + bmap_entry * block_size + index_in_block`, returns the child file, and adds `BDRV_BLOCK_RECURSE` for static images.

Reads iterate by VDI block boundaries. `vdi_co_preadv()` uses the bmap rwlock to read each block-map entry, zero-fills unallocated/discarded ranges, or reads from the child at the mapped physical offset. It uses a local concatenated `QEMUIOVector` per chunk.

Writes allocate on demand. `vdi_co_pwritev()` walks block boundaries, checks the bmap under read lock, upgrades to write lock for unallocated blocks, assigns the next physical block index from `header.blocks_allocated`, increments the header count, builds a full cluster buffer with unwritten parts zeroed, writes the entire new cluster while holding write-side bmap protection, and records the first/last modified bmap entries. Existing blocks are written directly as subranges. After successful data writes that allocated blocks, it writes the updated header and the affected aligned sectors of the block map. On data-write failure it returns before persisting header/map changes, leaving the in-memory map changed only for the failed open instance.

Creation is handled by `vdi_co_do_create()`. It validates size, preallocation mode, static-image support, optional cluster-size support, and maximum disk size; opens the protocol file through a `BlockBackend`; calculates block count and sector-aligned bmap size; writes a QEMU VDI header with generated image and snapshot UUIDs; writes a bmap filled with physical indices for static images or `VDI_UNALLOCATED` for dynamic images; and truncates static images to include all data blocks. Legacy create options create/open the file layer, translate `static` to QAPI `preallocation=metadata`, silently round size to sector size, and call the QAPI create path.

`vdi_close()` frees the bmap and removes the migration blocker. `vdi_has_zero_init()` returns the child zero-init status for static images and true for dynamic images because unallocated blocks read as zero.

Important risks and invariants:
- Only 512-byte sectors and 1 MiB VDI blocks are supported in the default build.
- Parent/link UUIDs are rejected, so VDI snapshots/backing chains are unsupported.
- Live migration is blocked for any VDI node.
- The code uses `CoRwlock` for block-map changes; header and bmap persistence must remain ordered after new cluster writes.
- Static images can report recursive block status because all payload blocks are mapped.
