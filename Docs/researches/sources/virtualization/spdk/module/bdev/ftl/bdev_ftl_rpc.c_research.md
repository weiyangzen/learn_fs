# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl_rpc.c

## Purpose
Provides JSON-RPC methods for FTL bdev lifecycle, unmap, statistics, and runtime properties.

## Main Entry Points
- `bdev_ftl_create` decodes FTL config, applies defaults, sets create mode when UUID is null, checks name conflicts, and starts or defers creation.
- `bdev_ftl_delete` unregisters an FTL bdev with optional fast shutdown.
- `bdev_ftl_unmap` submits an FTL management unmap range.
- `bdev_ftl_get_stats` returns per-stat-type read/write/error counters.
- `bdev_ftl_get_properties` delegates JSON property output to the FTL library.
- `bdev_ftl_set_property` sets a named property value.

## Internal Mechanics
Create initializes `spdk_ftl_conf` from defaults, then overlays RPC parameters. Successful create returns an object containing `name` and `uuid`; deferred create returns a string noting deferred creation. Stats output iterates all `FTL_STATS_TYPE_MAX` entries and emits named objects for user, compaction, GC, metadata base, metadata cache, and L2P counters.

## Dependencies
Uses SPDK JSON-RPC, bdev module utilities, string/log helpers, generated RPC autogen contexts, and `bdev_ftl.h`.

## Risks and Notes
Create treats `-ENODEV` specially as deferrable but reports most other failures as JSON-RPC internal errors. Stats context owns dynamically allocated memory and an FTL bdev descriptor that is closed by the shared action helper.
