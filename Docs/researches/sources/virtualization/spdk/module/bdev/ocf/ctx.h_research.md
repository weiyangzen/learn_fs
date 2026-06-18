# File Research: sources/virtualization/spdk/module/bdev/ocf/ctx.h

This header declares the SPDK OCF context interface and queue/cache-context helpers. It exports the global `ocf_ctx_t vbdev_ocf_ctx`, constants used by the OCF adapter, and `struct vbdev_ocf_cache_ctx`.

`vbdev_ocf_cache_ctx` holds the management OCF queue and an atomic reference count. The header declares get/put helpers, context init/cleanup, and wrappers for OCF normal and management queue creation/destruction.

The queue wrapper comments describe them as thread-safe creation/deletion adapters, giving the rest of the OCF bdev code a single include point for OCF queue lifecycle.
