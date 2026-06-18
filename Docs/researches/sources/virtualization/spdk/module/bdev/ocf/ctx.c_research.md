# File Research: sources/virtualization/spdk/module/bdev/ocf/ctx.c

This file creates the SPDK-backed OCF context used by the OCF virtual bdev module. It supplies OCF data operations, cleaner operations, logging, queue wrappers, and cache-context reference helpers, then calls `ocf_ctx_create()`/`ocf_ctx_put()` for module init/cleanup.

The data callbacks allocate `bdev_ocf_data` plus page-aligned DMA buffers, free iov buffers, implement no-op mlock/munlock, flatten iovecs into linear buffers, copy linear buffers back to iovecs, zero ranges, seek within data objects, copy between data objects, and securely erase memory through `env_memset()`. These callbacks are how OCF manipulates SPDK/DMA-backed data buffers.

Cleaner integration stores a management queue and a poller in `cleaner_priv`. `kick` registers a poller on the cache creation thread; the poller runs the OCF cleaner when the next-run timestamp has arrived. Completion schedules the next run based on OCF's interval. Stop unregisters the poller and frees private state.

The logger callback maps OCF log levels to SPDK log levels and uses `spdk_vlog()` without SPDK source-location decoration. Queue create/put wrappers currently call OCF queue APIs directly but centralize the integration point. Cache context refcounting uses environment atomics and frees the context at zero.

Important invariants include correct `seek` advancement for OCF data objects, DMA allocation/free symmetry, cleaner poller lifetime tied to OCF cleaner private data, and `vbdev_ocf_ctx` being non-null only between successful init and cleanup.
