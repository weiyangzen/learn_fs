# File Research: sources/virtualization/spdk/module/accel/iaa/accel_iaa.c

## Purpose

Implements an SPDK accel compression backend for Intel IAA/IDXD devices.

## Main Responsibilities

- Registers accel module `"iaa"` after startup RPC enablement.
- Configures IDXD in user mode.
- Probes IAA devices and allocates per-thread IDXD channels.
- Submits deflate compression/decompression work to IDXD IAA operations.
- Queues tasks on `-EBUSY` and retries from poller.
- Registers IAA tracepoints for submit/complete counts.
- Writes config JSON for `iaa_scan_accel_module`.

## Supported Operations

- `SPDK_ACCEL_OPC_COMPRESS`
- `SPDK_ACCEL_OPC_DECOMPRESS`

## Supported Algorithms

- `SPDK_ACCEL_COMP_ALGO_DEFLATE`
- Level range returns `0/0`.

## Key Control Flow

- `accel_iaa_enable_probe()` sets IDXD config to user mode and adds the module.
- `accel_iaa_init()` probes devices matching IAA IDs and registers the IO device.
- `_process_single_task()` maps SPDK compress/decompress tasks to `spdk_idxd_submit_compress` or `spdk_idxd_submit_decompress`.
- `iaa_submit_tasks()` queues tasks if channel is busy.
- `idxd_poll()` processes completions and retries queued tasks.

## Notes / Risks

- Contains a TODO for iovec support and asserts if source/destination iovcnt exceeds 1.
- Device selection is NUMA-local round-robin and may fail if no local device/channel is available.
- Only user mode is supported by this module at present.
