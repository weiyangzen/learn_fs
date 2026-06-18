# File Research: sources/virtualization/qemu/block/qcow.c

## Purpose
Implements QEMU's legacy `qcow` v1 image format driver. It supports sparse copy-on-write allocation, backing files, compressed clusters, deprecated AES-CBC encryption, image creation, image reads/writes, block status, and making an image empty.

## Main Entry Points
- `qcow_probe()` detects qcow v1 headers.
- `qcow_open()` opens the file child, validates the header, initializes encryption if present, loads the L1 table, allocates L2/cache buffers, reads the backing filename, blocks migration, and initializes the coroutine lock.
- `qcow_co_preadv()` reads guest data from allocated clusters, compressed clusters, backing files, or zero-fill.
- `qcow_co_pwritev()` allocates clusters as needed and writes plaintext or encrypted data.
- `qcow_co_pwritev_compressed()` compresses full clusters and stores compressed cluster descriptors.
- `qcow_co_block_status()` reports allocated/compressed/mappable state.
- `qcow_make_empty()` clears the L1 table, truncates after it, and resets the L2 cache.
- `qcow_co_create()` and `qcow_co_create_opts()` create new qcow v1 images.
- `qcow_close()` releases encryption, tables, caches, and migration blocker.

## Internal Mechanics
The format uses a big-endian header, an L1 table of L2-table offsets, and L2 tables containing cluster descriptors. `get_cluster_offset()` is the central lookup/allocation routine. It loads or allocates L2 tables, keeps a 16-entry L2 cache with hit counts, allocates data clusters at aligned EOF, handles conversion from compressed to normal clusters for partial overwrites, initializes unwritten encrypted sectors with encrypted zeros, and writes L1/L2 updates synchronously.

Reads lock the driver state while resolving cluster mappings. Unallocated clusters read from the backing file when present or return zeroes. Compressed clusters are read and inflated into `cluster_cache`. Normal clusters are read from the file; encrypted images decrypt data after reading. Multi-iov reads are staged through an aligned temporary buffer.

Writes invalidate the compressed cluster cache, stage encrypted or multi-iov data into a temporary buffer, allocate normal clusters through `get_cluster_offset()`, encrypt in place when needed, and write to the backing file child. Compressed writes deflate a cluster with raw zlib, fall back to normal writes if compression is ineffective, otherwise allocate a compressed descriptor and write compressed bytes.

Image creation writes a v1 header, optional backing filename, and zeroed L1 table. Backing images use 512-byte clusters to avoid copying unmodified sectors; standalone images use 4 KiB clusters.

## Dependencies
Uses zlib, QEMU crypto block helpers, QAPI create-option visitors, block backend creation, block debug events, migration blockers, aligned allocation, qdict option conversion, and shared block crypto option helpers.

## Filesystem/Block Relevance
This is a legacy sparse COW image implementation. It demonstrates classic table-based virtual disk allocation, backing-chain reads, compressed cluster representation, and historical in-format encryption handling.

## Risks and Notes
- qcow v1 blocks live migration through a migration blocker.
- AES-CBC encrypted qcow is deprecated and rejected in system emulators when the block whitelist is active.
- The format cannot store a backing format; create-options only validate the requested backing format.
- Request alignment is forced to 512 bytes, partly to keep encrypted-sector handling safe.
- Compressed cluster cache is single-cluster and disabled on writes.
- Many metadata updates are synchronous to preserve consistency after L1/L2 changes.
