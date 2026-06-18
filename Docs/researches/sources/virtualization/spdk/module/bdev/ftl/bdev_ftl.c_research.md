# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.c

## Purpose
Wraps `spdk_ftl_dev` as an SPDK bdev. It handles FTL module initialization, bdev creation/deletion, deferred creation when base devices are absent, I/O dispatch, stats/properties helpers, and JSON configuration.

## Main Entry Points
- `bdev_ftl_create_bdev()` opens base/cache bdevs, allocates an `ftl_bdev`, and starts `spdk_ftl_dev_init()`.
- `bdev_ftl_delete_bdev()` validates the named bdev belongs to the FTL module, configures fast shutdown, and unregisters it.
- `bdev_ftl_defer_init()` stores a copied FTL config for later examine-time creation.
- `bdev_ftl_unmap()`, `bdev_ftl_get_stats()`, `bdev_ftl_get_properties()`, and `bdev_ftl_set_property()` run management actions on an existing FTL bdev.
- Module callbacks initialize/finalize the FTL library and examine deferred init entries.

## Internal Mechanics
I/O support is limited to READ, WRITE, UNMAP, and FLUSH. Reads first acquire a bdev buffer, then call `spdk_ftl_readv()`. Writes and unmaps call the matching FTL vector APIs. Flush completes successfully without forwarding. FTL completion return codes map `0` to success, `-EAGAIN`/`-ENOMEM` to bdev NOMEM, and other errors to failed.

Creation keeps descriptors for both base and cache bdevs so the underlying devices stay open. `bdev_ftl_create_cb()` queries FTL attributes/config, fills bdev geometry, UUID, optimal I/O boundary, and registers the bdev. On partial failure after FTL device creation, it disables fast shutdown and frees the FTL device asynchronously before reporting the original error.

Management actions share `struct bdev_ftl_action`, which opens the named bdev, verifies module ownership, stores callback state, and closes the descriptor on completion.

## Dependencies
Uses SPDK bdev, thread/env/JSON/string utilities, `spdk/ftl.h`, and internal FTL stats structures from `ftl_core.h`.

## Risks and Notes
`bdev_ftl_create_bdev()` unconditionally opens `conf->cache_bdev`; callers/config defaults must provide a usable cache bdev string. Deferred init iterates one entry per examine callback and removes an entry once creation is attempted on a present base. The generic action helper invokes the callback synchronously on setup failure, so RPC callers must tolerate immediate completion.
