# File Research: sources/virtualization/spdk/lib/blob/blob_bs_dev.c

`blob_bs_dev.c` implements a read-only `spdk_bs_dev` adapter backed by an SPDK blob. It is used for blobstore layering cases such as snapshots or copy-on-write backing devices.

Write, writev, writev_ext, write_zeroes, and unmap are hard-fail paths: they invoke the callback with `-EPERM` and assert false. Read paths wrap `spdk_blob_io_read()`, `spdk_blob_io_readv()`, and `spdk_blob_io_readv_ext()` and forward completion through `blob_bs_dev_read_cpl()`.

`zero_trailing_bytes()` handles cases where the requested child blob range extends past the backing blob’s block count. It zeroes the trailing payload bytes and reduces the LBA count before submitting the backing blob read, so reads beyond the backing extent return zero-filled data rather than reading invalid backing ranges.

Destroy closes the backing blob asynchronously and frees the adapter on close completion. Errors during close are logged before freeing.

Copy-on-write helpers expose whether a range is zeroes, whether a range is valid, LBA translation to an allocated blob cluster or backing device, and degraded state. `is_zeroes` and `translate_lba` check whether the blob IO unit is allocated locally; if not, they consult the backing `bs_dev` using translated backing LBAs. `is_range_valid` treats the blob’s active cluster count as the valid range.

`bs_create_blob_bs_dev()` allocates the adapter, sets block count from active clusters and IO units per cluster, sets block size to blobstore IO-unit size, wires read-only operations and COW query callbacks, stores the blob pointer, and returns the embedded `spdk_bs_dev`.

Research notes: this adapter deliberately denies mutation and is intended for backing-device semantics. The trailing-zero loop is important for expanded children over smaller backing blobs; changes there should be audited carefully for multi-iovec zeroing behavior.
