# File Research: sources/virtualization/spdk/lib/idxd/idxd.c

`idxd.c` is the common SPDK Intel IDXD/DSA/IAA datapath implementation. It is backend-agnostic: user-mode PCI and kernel accel-config backends register `spdk_idxd_impl` objects, while this file owns channel allocation, descriptor pools, batching, address translation, operation submission, completion polling, and DIF/DIX validation.

Global implementation selection is explicit through `spdk_idxd_set_config(bool kernel_mode)`, which chooses the registered `user` or `kernel` implementation. Once devices are initialized, changing implementations is rejected. Probing and detach delegate to the selected backend’s `probe()` and `destruct()` hooks.

Each `spdk_idxd_io_channel` gets a descriptor pool, completion/operation pool, portal address/offset, and for DSA a pool of preallocated batch objects. Channel count is limited by `chan_per_device`, guarded by `num_channels_lock`, and portal offsets are distributed by channel. Address translation uses virtual addresses when PASID/shared virtual addressing is enabled; otherwise it uses `spdk_vtophys()` and rejects non-contiguous mappings that cannot satisfy a descriptor segment.

Submission uses 64-byte descriptor writes via `movdir64b()` after a write memory barrier. Regular descriptors come from `ops_pool`; batch descriptors are built inside `idxd_batch` objects and later submitted as either a single converted descriptor or an `IDXD_OPCODE_BATCH` descriptor. Batches flush automatically at `IDXD_MIN_BATCH_FLUSH` entries and are also submitted from `spdk_idxd_process_events()` if still open.

DSA operations include copy, dualcast, compare, fill, CRC32C, copy+CRC32C, raw descriptor submission, DIF check/insert/strip, and DIX generate. Copy and compare walk source/destination iovecs with `spdk_ioviter`, split on physical contiguity boundaries, and use parent/child completion counting so one logical user callback fires after all split descriptors complete. Dualcast enforces 4 KiB destination alignment. CRC operations chain seeds through prior completion records and copy only the final CRC to the caller.

IAA operations include compression and decompression. The current implementation only supports simple single-buffer compression/decompression cases; vectored support returns `-EINVAL`. Compression uses the device AECS address and IAA flags, and completion records can return the output size.

DIF/DIX helpers validate SPDK DIF context restrictions before building descriptors. Supported cases are narrow: zero data offset, zero guard seed, PI format 16, metadata sizes 8 or 16 depending on operation, interleaved metadata for DIF operations, separate metadata for DIX generate, 512/4096 data blocks plus 520/4104 interleaved forms, and required guard/app/ref tag flags for insert/generate. Buffer lengths must align to block or data-block sizes because DSA handles each iovec independently.

Completion polling scans `ops_outstanding` in order, stops at the first incomplete record, handles up to `IDXD_MAX_COMPLETIONS`, checks failure status, dumps software error registers via the backend, writes CRC/output-size results, maps compare results and DIF errors, returns completed regular ops to `ops_pool`, decrements batch reference counts, frees batches back to the pool, and invokes callbacks after operation accounting is complete.

Research notes: key correctness points are descriptor lifetime, batch refcounting, parent/child count handling for split operations, PASID-vs-physical-address behavior, and strict DIF/DIX parameter validation. Some error paths decrement `chan->batch->index` to roll back partially prepared descriptors, so edits to operation builders must keep `count` accurate.
