# File Research: sources/virtualization/spdk/app/fio/bdev/fio_plugin.c

## Purpose
Implements the `spdk_bdev` fio ioengine. It lets fio jobs issue read, write, trim, flush, zone append, zone report, and zone reset operations through SPDK's bdev layer.

## Main Entry Points
- `spdk_fio_setup()` validates fio thread mode, initializes SPDK once, expands `*` to all leaf bdevs, resolves file names to bdevs, and sets fio file sizes.
- `spdk_fio_init()` creates a per-fio-thread SPDK thread and opens bdev descriptors/channels.
- `spdk_fio_queue()` maps fio directions to `spdk_bdev_read()`, `spdk_bdev_write()`, `spdk_bdev_unmap()`, `spdk_bdev_flush()`, or `spdk_bdev_zone_append()`.
- `spdk_fio_getevents()` polls the SPDK thread until enough fio completions are available or timeout expires.
- `spdk_fio_report_zones()`, `spdk_fio_reset_wp()`, `spdk_fio_get_zoned_model()`, and `spdk_fio_get_max_open_zones()` provide fio ZBD integration when supported by the fio version.
- `spdk_fio_register()` and `spdk_fio_unregister()` register/unregister the fio engine.

## Internal Mechanics
A dedicated initialization/poll thread initializes SPDK env, loads JSON config, starts SPDK subsystems, optionally opens an RPC listener, and polls SPDK threads. Each fio worker gets a `spdk_fio_thread` with a SPDK thread, completion queue, and a list of opened bdev targets.

Synchronous calls that must run on the SPDK app thread use `spdk_fio_sync_run_oat()`, a condition-variable bridge that sends a message to the app thread and waits for completion. This is used for setup and some bdev capability queries.

I/O completion stores completed fio `io_u` pointers in the thread's `iocq`. `-ENOMEM` from bdev submission maps to `FIO_Q_BUSY`; other submission errors complete the fio I/O with an errno.

Zoned support converts SPDK bdev zone descriptors into fio `zbd_zone` structures, supports optional initial zone reset, and can replace writes with zone append when the target supports `SPDK_BDEV_IO_TYPE_ZONE_APPEND`.

## Options
Supports `spdk_conf`, `spdk_json_conf`, `spdk_mem`, `spdk_single_seg`, `log_flags`, `initial_zone_reset`, `zone_append`, `env_context`, and `spdk_rpc_listen_addr`.

## Dependencies
Depends on SPDK bdev, bdev zone, event/subsystem initialization, RPC, thread, env, DMA allocation, and fio plugin APIs. Conditional behavior depends on `FIO_IOOPS_VERSION`.

## Filesystem/Block Relevance
This is the primary fio bridge for benchmarking SPDK's generic block-device abstraction, including zoned bdevs and module-backed devices.

## Risks and Notes
- Requires fio `thread=1`.
- Fio daemon mode is rejected unless stdout/stderr are safely redirected to `/dev/null`.
- SPDK env is global and initialized once across fio jobs.
- The background poll loop is central to completions and app-thread message progress.
- Zoned callbacks are compiled only for sufficiently new fio versions.
