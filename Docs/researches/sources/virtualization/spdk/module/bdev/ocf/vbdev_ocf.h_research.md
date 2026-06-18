# File Research: sources/virtualization/spdk/module/bdev/ocf/vbdev_ocf.h

This header defines the main data model and public internal API for the OCF virtual bdev module. It exposes the structures shared by OCF implementation, helpers, stats/RPC code, and volume integration.

`struct vbdev_ocf_qctx` maps an SPDK thread/channel to an OCF queue, SPDK poller, parent vbdev, and cache/core bdev channels. `struct vbdev_ocf_state` tracks clean delete, finish, reset, started, starting, and last stop status. `struct vbdev_ocf_config` wraps OCF cache, attach, and core management configs plus the load flag.

`struct vbdev_ocf_mngt_ctx` holds the current asynchronous management path, optional poller step, timeout, status, and completion callback. `struct vbdev_ocf_base` represents a cache or core base bdev with name, descriptor, open/claim state, management channel, parent, and opening thread. `struct vbdev_ocf` ties all of this to OCF cache/core handles, cache context, flush state, exposed SPDK bdev, metadata UUID buffer, and global-list link.

The API declares construct, lookup, base lookup, delete, clean delete, cache-mode update, sequential cutoff update, and foreach traversal. It intentionally exposes enough state for neighboring OCF files to operate on queues, stats, and management operations, so callers must respect the state flags and management-context rules.
