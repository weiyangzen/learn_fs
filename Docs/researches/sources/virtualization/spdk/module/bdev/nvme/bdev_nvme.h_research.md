# File Research: sources/virtualization/spdk/module/bdev/nvme/bdev_nvme.h

This is the private header for SPDK's NVMe bdev module. It defines shared state structures for NVMe bdev controllers, NVMe controller paths, namespaces, qpair/channel/poll-group objects, multipath I/O paths, async probe state, and module-internal control APIs used by the RPC, mDNS, CUSE, OPAL, and core bdev code.

The header documents the threading model explicitly. Namespace and controller fields are modified primarily on the app thread, while selected flags and ANA state are read on I/O threads as best-effort hints; stale reads are expected to converge through normal I/O failure/retry handling. Some shared bdev namespace/path state is protected by mutexes, especially namespace lists, multipath settings, error stats, and references.

`struct nvme_ctrlr` ties a SPDK NVMe controller to bdev-layer state: active path, reference count, reset/reconnect/failover flags, namespaces, OPAL device, admin pollers/interrupts, pending resets, parent `nvme_bdev_ctrlr`, path IDs, ANA log data, probe context, authentication keys, memory-domain types, and a mutex. `struct nvme_bdev` wraps an exposed SPDK bdev with NSID, parent controller group, multipath policy/selector, path list, OPAL flag, update state, and optional error stats.

Channel-side structures map SPDK I/O channels to NVMe qpairs and poll groups. `nvme_io_path` links a namespace to a qpair and optional per-path statistics. `nvme_bdev_channel` caches current path selection and retry state. `nvme_poll_group` wraps `spdk_nvme_poll_group`, optional accel channel, poller/interrupt, spin stats, and qpair list.

The declaration surface includes controller lookup/iteration, channel iteration helpers, JSON dump helpers, qpair access, hotplug control, discovery/mDNS start/stop/info, authentication key update, bdev-to-controller lookup, controller reset/enable/disable RPC operations, and preferred path update. Invariants center on app-thread mutation, mutex-protected shared lists/settings, and stable callback semantics for asynchronous operations.
