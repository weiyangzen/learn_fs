# File Research: sources/virtualization/spdk/lib/fsdev/fsdev.c

## Purpose
Implements SPDK's deprecated `fsdev` core registry and lifecycle layer. It manages filesystem-device modules, registered devices, names, descriptors, IO channels, shared channel resources, per-thread IO caches, and hot-remove/unregister flows.

## Main Responsibilities
- Maintains global `g_fsdev_mgr` with a mempool for `spdk_fsdev_io`, registered modules, registered fsdevs, an RB tree of names, initialization state, and a spinlock.
- Initializes and finishes the fsdev subsystem through `spdk_fsdev_initialize()` and `spdk_fsdev_finish()`.
- Registers JSON config emission via `spdk_fsdev_subsystem_config_json()`.
- Creates management channels with pre-populated per-thread `spdk_fsdev_io` caches to reduce mempool contention.
- Creates per-fsdev IO channels and deduplicates module shared resources per management channel.
- Registers/unregisters fsdevs, sends `fsdev_register` and `fsdev_unregister` notifications, and defers remove callbacks to descriptor owner threads.
- Opens and closes descriptors with SPDK-thread affinity and descriptor reference tracking.
- Submits fsdev IO to module `submit_request()` implementations, tracks outstanding counts, and completes user callbacks on the right thread.

## Key Data Structures
- `struct spdk_fsdev_mgr`: global subsystem state.
- `struct spdk_fsdev_mgmt_channel`: per-thread IO cache and shared resource list.
- `struct spdk_fsdev_shared_resource`: shared module channel plus outstanding IO and refcount.
- `struct spdk_fsdev_channel`: per-fsdev channel with submitted IO queue and outstanding count.
- `struct spdk_fsdev_desc`: open descriptor with event callback, owning thread, refs, and closed flag.

## Important Behavior
- `SPDK_LOG_DEPRECATION_REGISTER()` marks fsdev as being replaced in `v26.09`.
- Options are versioned by `opts_size`; `spdk_fsdev_set_opts()` enforces a minimum IO pool size based on cache size and SPDK thread count.
- `fsdev_io_complete()` defers completion if called inside module `submit_request()` to avoid recursive callback-driven IO submission.
- Unregister transitions through `UNREGISTERING` then `REMOVING`; open descriptors receive `SPDK_FSDEV_EVENT_REMOVE` asynchronously before final io_device unregister/destruct.
- `spdk_fsdev_unregister_by_name()` opens the device temporarily to verify module ownership before unregistering.

## Dependencies
Uses SPDK thread/io_device, mempool, notify, JSON, queue/RB-tree, spinlock, logging, and `spdk/fsdev_module.h` module callbacks.
