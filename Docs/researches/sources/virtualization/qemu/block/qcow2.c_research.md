# File Research: sources/virtualization/qemu/block/qcow2.c

## Role

This is QEMU's qcow2 block driver implementation. It registers `bdrv_qcow2` and supplies the driver entry points for probing, opening, closing, reads, writes, compressed I/O, zero/discard, copy range, resize, create, amend, snapshots, checks, metadata flushing, backing-file changes, persistent dirty bitmaps, and VM state storage.

The file is the coordinating layer for qcow2 format behavior. Refcount, cluster mapping, snapshot, cache, bitmap, crypto, and compression helper implementations live in adjacent qcow2 modules, but this file orchestrates their use and owns top-level format policy.

## Major Responsibilities

- Detect qcow2 images with `qcow2_probe()`.
- Parse qcow2 headers and header extensions in `qcow2_do_open()`.
- Validate format version, cluster geometry, feature bits, compression type, refcount table, L1 table, snapshot table, encryption mode, and external data-file semantics.
- Manage dirty/corrupt flags with `qcow2_mark_dirty()`, `qcow2_mark_clean()`, `qcow2_mark_corrupt()`, and `qcow2_mark_consistent()`.
- Configure runtime options: lazy refcounts, discard passthrough, overlap checking, cache sizing, cache-clean timer, and encryption options.
- Split guest I/O into cluster/subcluster-sized tasks and dispatch parallel `AioTaskPool` work where useful.
- Implement creation and option conversion for both legacy `QemuOpts` and QAPI `BlockdevCreateOptions`.
- Rewrite qcow2 headers with variable-length extensions in `qcow2_update_header()`.
- Resize images, including L1 growth/shrink, refcount shrink, metadata/data preallocation, raw external data-file invariants, and zero-fill-on-grow.
- Support downgrade/upgrade/amend flows for compat version, refcount width, lazy refcounts, LUKS options, external data-file metadata, and size.
- Emit corruption events and make the block node unusable after fatal corruption.

## Header Extension Handling

The file defines qcow2 extension magic values for end marker, backing format, feature table, crypto header, bitmaps, and external data file. `qcow2_read_extensions()` scans aligned extensions between the fixed header and backing-file area or first cluster end.

Known extensions populate state:

- backing format into `bs->backing_format` and `s->image_backing_format`
- feature table for better unsupported-feature diagnostics
- LUKS crypto header location and crypto context
- persistent dirty bitmap directory metadata
- external data-file name

Unknown extensions are preserved in `s->unknown_header_ext` so `qcow2_update_header()` can rewrite them later. Bitmap extensions are guarded by autoclear feature semantics; if bitmap support was not preserved by a prior writer, the file warns and requests header cleanup.

## Open Path

`qcow2_open()` opens the underlying file child, initializes coroutine lock state, then enters `qcow2_open_entry()` to run `qcow2_do_open()` under graph read lock and `s->lock`.

`qcow2_do_open()` performs the core format validation:

- Reads `QCowHeader` and converts big-endian fields.
- Accepts only qcow2 versions 2 and 3.
- Validates `cluster_bits` against `MIN_CLUSTER_BITS` and `MAX_CLUSTER_BITS`.
- Initializes version 2 defaults for feature fields, refcount order, and header length.
- Validates v3 header length and preserves unknown fixed-header tail bytes.
- Rejects unsupported incompatible feature bits after optionally reading feature names.
- Rejects corrupt images opened read/write except in check mode.
- Initializes standard or extended-L2 subcluster geometry.
- Validates refcount order and derives refcount width/max.
- Handles deprecated AES and LUKS crypto setup.
- Derives L2 size, refcount block geometry, compressed-size masks, virtual size, and table sizes.
- Validates refcount, snapshot, and active L1 table offsets/sizes through `qcow2_validate_table()`.
- Loads and endian-converts the active L1 table.
- Applies runtime options and initializes refcount handling.
- Reads header extensions, external data-file state, backing filename, snapshots, and dirty bitmaps.
- Clears unknown autoclear bits when writable.
- Repairs dirty writable images by running `qcow2_co_check_locked()` with fix flags.

Failure cleanup is extensive: external child references, unknown header data, snapshots, refcount state, L1 table, cache timer, metadata caches, crypto state, and crypto options are released.

## Runtime Options And Caches

`qcow2_runtime_opts` defines mutable driver options for lazy refcounts, discard behavior, overlap checks, L2/refcount cache sizing, cache-clean interval, and encryption secrets.

`read_cache_sizes()` derives L2 and refcount cache sizes from combined or separate cache options. It enforces minimum entries and validates L2 cache entry size as a power of two between 512 bytes and cluster size.

`qcow2_update_options_prepare()` builds replacement caches, flushes old caches, parses overlap templates (`none`, `constant`, `cached`, `all`), derives discard policy, handles lazy-refcount transitions, validates `discard-no-unref`, and prepares crypto open options. Commit swaps caches/options and restarts the cache-clean coroutine; abort destroys prepared caches and crypto options.

The cache-clean timer is coroutine-based and only active when `cache_clean_interval > 0`. A detach/attach AIO context pair stops and restarts it across context changes.

## Read Path

`qcow2_co_preadv_part()` loops across the guest request, obtains host mapping with `qcow2_get_host_offset()`, and handles each subcluster type:

- zero subclusters or unallocated-without-backing: fill the output iovec with zeroes
- unallocated-with-backing: read from backing file
- compressed: call `qcow2_co_preadv_compressed()`
- normal encrypted: read into an aligned temporary buffer and decrypt
- normal unencrypted: read directly from `s->data_file`

Large requests are split into parallel tasks using `AioTaskPool` with `QCOW2_MAX_WORKERS`.

## Write Path

`qcow2_co_pwritev_part()` loops over the write request, allocates or maps host space with `qcow2_alloc_host_offset()`, runs pre-write metadata overlap checks, and dispatches write tasks.

`qcow2_co_pwritev_task()` handles encryption, optional zero initialization of newly allocated physical space, COW-region merge optimization, direct data write when not merged, then links L2 metadata with `qcow2_alloc_cluster_link_l2()`. On error it aborts outstanding `QCowL2Meta` structures through `qcow2_handle_l2meta()`.

The write path uses `s->lock` to serialize metadata decisions while releasing it for actual data I/O.

## Compressed I/O

`qcow2_co_pwritev_compressed_part()` rejects external data-file images, requires cluster-aligned writes except for the final partial cluster, and splits work by cluster.

`qcow2_co_pwritev_compressed_task()` pads a final short cluster with zeroes, compresses via `qcow2_co_compress()`, falls back to normal writes on compression buffer exhaustion, allocates a compressed cluster descriptor, checks overlap, and writes compressed bytes.

`qcow2_co_preadv_compressed()` parses the compressed L2 entry, reads compressed bytes from the qcow2 file, decompresses into a full-cluster buffer, and copies the requested slice to the caller.

## Zero, Discard, Copy Range

`qcow2_co_pwrite_zeroes()` uses subcluster alignment. For unaligned head/tail cases it first verifies surrounding bytes already read as zero, waits for dependent allocations, rechecks mapping type, then calls `qcow2_subcluster_zeroize()`.

`qcow2_co_pdiscard()` rejects unsafe v2-with-backing cases because discarding could expose stale backing data, ignores most partial-cluster discards, and delegates aligned work to `qcow2_cluster_discard()`.

`qcow2_co_copy_range_from()` maps qcow2 source ranges to backing/data/zero sources and rejects compressed clusters. `qcow2_co_copy_range_to()` allocates destination host space and copies into `s->data_file`, then links metadata.

## Creation

`qcow2_co_create_opts()` translates legacy create options into QAPI create options, creates protocol-level image and optional external data file, validates `keep-data-file` constraints, rounds size to sector size, and delegates to `qcow2_co_create()`.

`qcow2_co_create()` creates a minimal qcow2 file:

- Validates size, version, cluster size, extended L2, preallocation, backing options, lazy refcounts, refcount bits, external data file, raw data-file mode, and compression type.
- Writes a zero-sized header with one refcount table cluster.
- Writes an initial refcount table pointing at the first refcount block.
- Opens the new image as qcow2, allocates header/refcount clusters, sets external data-file metadata, rewrites the full header, resizes to requested virtual size, optionally sets backing file, optionally creates encryption headers, then reopens/flushed through lower layers.

Compatibility constraints are strict: extended L2, external data files, non-16-bit refcounts, lazy refcounts, and non-zlib compression require version 3.

## Header Rewrite

`qcow2_update_header()` rebuilds the first cluster from in-memory state. It writes the fixed header, unknown fixed fields, backing-format extension, external-data-file extension, crypto-header extension, feature table when cluster size permits, bitmap extension, unknown extensions, end marker, and backing filename.

The function preserves unknown extension data but may fail with `-ENOSPC` because qcow2 stores all header variable data in the first cluster. It validates compression feature consistency before writing.

## Resize And Preallocation

`qcow2_co_truncate()` handles both shrink and grow.

Shrink path:

- Rejects preallocation modes.
- Discards cropped clusters.
- Shrinks L1 table and refcount table.
- Optionally truncates the underlying file tail after finding the last referenced cluster.

Grow path:

- Grows L1 table.
- Forces metadata preallocation for `data-file-raw` if needed.
- Handles external data-file resize.
- Handles metadata-only preallocation through `preallocate_co()`.
- Handles falloc/full preallocation by growing refcount coverage, allocating data clusters, resizing the underlying file, and entering L2 mappings.
- Applies zero-write semantics for newly exposed regions.
- Flushes metadata for preallocation.
- Updates `bs->total_sectors`, header size field, VM-state L1 index, and cache sizing.

`qcow2_refcount_metadata_size()` and `qcow2_calc_prealloc_size()` estimate metadata required for refcount blocks/table, L1/L2 tables, and fully allocated image size.

## Emptying And Flush

`qcow2_make_empty()` has a fast path for v3 images without snapshots, bitmaps, LUKS, external data files, or oversized initial metadata. That path marks the image dirty, rewrites L1/refcount structures near the start of the file, reinitializes in-memory refcount state, marks clean, and truncates the image. Otherwise it falls back to discarding guest clusters.

`qcow2_co_flush_to_os()` serializes and writes metadata caches with `qcow2_write_caches()`.

## Metadata Reporting

`qcow2_measure()` estimates required and fully allocated sizes from create options and optional input image block status. It accounts for cluster size, refcount bits, extended L2 entry size, LUKS payload offset, preallocation mode, backing-file conservatism, and persistent dirty bitmap size.

`qcow2_co_get_info()` returns cluster/subcluster size, VM-state offset, and dirty state. `qcow2_get_specific_info()` returns qcow2-specific QAPI info including compat level, lazy refcounts, corrupt state, extended L2, refcount bits, bitmaps, external data file, raw data-file flag, compression type, and encryption details.

## Amend, Upgrade, Downgrade

`qcow2_amend_options()` supports:

- compat upgrade/downgrade
- LUKS encryption option amendment
- refcount width change
- data-file metadata name update
- data-file-raw autoclear flag update
- lazy-refcount enable/disable
- exact resize

Upgrade to v3 may rewrite snapshots so required v3 extra data is present. Downgrade to v2 rejects non-16-bit refcounts, external data files, unsafe snapshots, incompatible features, and zstd-compressed clusters; it expands zero clusters and rewrites the header as v2.

`qcow2_co_amend()` is the blockdev-amend path for LUKS encryption options only.

## Corruption Handling

`qcow2_signal_corruption()` suppresses repeated events, emits a `BLOCK_IMAGE_CORRUPTED` QAPI event, marks fatal writable images corrupt, and sets `bs->drv = NULL` to make the block node unusable. Read-only images treat detected corruption as non-fatal.

## Notable Internal Assumptions

- The graph read lock annotations are used heavily because coroutine I/O paths interact with block graph state.
- `s->lock` protects qcow2 metadata state, while actual data I/O often runs with the lock released.
- Some invariants use `assert()` or `abort()` for impossible states, especially after allocation/refcount assumptions.
- Comments call out unresolved or limited behavior: bitmap generation tracking after migration, data preallocation TODO in `preallocate_co()`, copy-range refcount-sharing optimization TODO, and compressed-sector placement XXX.
