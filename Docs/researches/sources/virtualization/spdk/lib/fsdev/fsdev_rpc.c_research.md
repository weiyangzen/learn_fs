# File Research: sources/virtualization/spdk/lib/fsdev/fsdev_rpc.c

## Purpose
Provides runtime JSON-RPC handlers for fsdev subsystem options.

## RPCs
- `fsdev_get_opts`: takes no params, calls `spdk_fsdev_get_opts()`, and returns `fsdev_io_pool_size` plus `fsdev_io_cache_size`.
- `fsdev_set_opts`: decodes optional `fsdev_io_pool_size` and `fsdev_io_cache_size`, starts from current options, updates them, and calls `spdk_fsdev_set_opts()`.

## Dependencies
Uses SPDK JSON-RPC, logging, `spdk/fsdev.h`, and generated `rpc_fsdev_set_opts_ctx` from `spdk_internal/rpc_autogen.h`.
