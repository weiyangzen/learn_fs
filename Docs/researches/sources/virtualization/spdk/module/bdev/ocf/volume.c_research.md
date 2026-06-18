# File Research: sources/virtualization/spdk/module/bdev/ocf/volume.c

This file adapts SPDK bdevs to OCF volume operations. It registers an OCF volume type named `SPDK_block_device` whose private data is a `struct vbdev_ocf_base *`, and whose forward operations translate OCF read/write/flush/discard requests into SPDK bdev I/O.

`vbdev_ocf_volume_open()` stores the base pointer in the OCF volume private area. It either uses an explicit `opts` pointer or resolves a base object by UUID data via `vbdev_ocf_get_base_by_name()`. Close is a no-op. `vbdev_ocf_volume_get_length()` returns `blocklen * blockcnt` from the resolved base bdev. `vbdev_ocf_volume_get_max_io_size()` currently returns a fixed 131072 byte maximum.

The central path is `vbdev_forward_io()`. It gets the base object from volume private data, gets the OCF data object from the forward token, selects an SPDK I/O channel with `vbdev_forward_get_channel()`, and submits `spdk_bdev_readv()` or `spdk_bdev_writev()`. Management queues use the base management channel; normal queues use the queue private `vbdev_ocf_qctx` and choose cache or core channel based on `base->is_cache`.

Partial data forwarding is handled by `get_starting_vec()` and `initialize_cpy_vector()`. When the requested byte count is smaller than the OCF data buffer, the code finds the starting iovec for the given offset, allocates a temporary iovec array with `env_malloc()`, and creates a trimmed view into the original iovecs. The completion callback frees this temporary iovec array when used. Submission failures manually call `ocf_forward_end()` because SPDK completion will not run.

Flush and discard are direct translations. `vbdev_forward_flush()` submits a full-device SPDK flush over `blockcnt * blocklen` bytes. `vbdev_forward_discard()` submits `spdk_bdev_unmap()` for the requested byte address and length. Both return `-OCF_ERR_NO_MEM` on `-ENOMEM` submission failure and `-OCF_ERR_IO` otherwise.

`vbdev_forward_io_simple()` exists for OCF contexts where no queue is available. It allocates a small context, obtains an I/O channel with `spdk_bdev_get_io_channel()`, submits read/write on the OCF data iovs, and releases the channel in `vbdev_forward_io_simple_cb()`.

`vbdev_ocf_volume_init()` registers the OCF volume type against `vbdev_ocf_ctx` and `SPDK_OBJECT`; cleanup unregisters it. The implementation assumes byte-addressed OCF requests are aligned well enough for the underlying bdev calls and relies on OCF/SPDK higher layers for lifecycle synchronization of the base descriptors and channels.
