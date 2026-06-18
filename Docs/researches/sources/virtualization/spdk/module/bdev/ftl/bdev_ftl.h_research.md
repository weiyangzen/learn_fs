# File Research: sources/virtualization/spdk/module/bdev/ftl/bdev_ftl.h

## Purpose
Declares the internal FTL bdev control interface shared by the core FTL bdev module and its RPC implementation.

## Main Contents
- `struct ftl_bdev_info` returns the created bdev name and UUID.
- `struct rpc_ftl_stats_ctx` carries an open FTL descriptor, JSON-RPC request, and `struct ftl_stats`.
- `ftl_bdev_init_fn` is the async create callback type.
- Prototypes cover create, delete, deferred init, unmap, get stats, get properties, and set property.

## Dependencies
Includes SPDK bdev module and FTL APIs plus `ftl_core.h` for stats.

## Risks and Notes
The header couples RPC context directly to core module declarations through `rpc_ftl_stats_ctx`, so changes to stats reporting affect both layers.
