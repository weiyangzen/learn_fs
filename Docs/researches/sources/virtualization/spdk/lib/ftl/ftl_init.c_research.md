# File Research: sources/virtualization/spdk/lib/ftl/ftl_init.c

## Purpose
Implements FTL device allocation, startup, shutdown, and core-thread setup.

## Startup
- `allocate_dev()` allocates `spdk_ftl_dev`, initializes properties and config, creates or selects the core thread, initializes IO queues, and initializes user/GC writers.
- `spdk_ftl_dev_init()` creates callback context, allocates the device, and starts the management startup sequence via `ftl_mngt_call_dev_startup()`.
- `dev_init_cb()` handles startup retry when `dev->init_retry` is set, otherwise reports final status and frees failed devices.

## Shutdown
- `spdk_ftl_dev_free()` calls management shutdown via `ftl_mngt_call_dev_shutdown()`.
- `dev_free_cb()` frees the device on successful shutdown and invokes the user callback.
- `free_dev()` tears down the core thread when it was created from `core_mask`, deinitializes config/properties, and frees memory.

## Core Thread
If `conf.core_mask` is set, a named `ftl_core_thread` is created on the parsed cpuset; otherwise the current SPDK thread is used.

## Dependencies
Uses SPDK thread/cpuset/bdev/config APIs, FTL core/IO/band/debug/NV-cache/writer/utils, and management startup/shutdown.
