# File Research: sources/virtualization/spdk/module/accel/ioat/accel_ioat.c

## Purpose

Implements an SPDK accel backend for Intel IOAT DMA engines.

## Main Responsibilities

- Registers accel module `"ioat"` when enabled.
- Probes IOAT PCI devices, claims them, and tracks PCI devices for detach.
- Allocates one unallocated IOAT channel/device per SPDK IO channel.
- Supports copy and fill tasks using IOAT descriptor builders.
- Flushes IOAT descriptors after batched submit.
- Polls completions through `spdk_ioat_process_events`.
- Writes config JSON for `ioat_scan_accel_module`.

## Supported Operations

- `SPDK_ACCEL_OPC_COPY`
- `SPDK_ACCEL_OPC_FILL`

## Key Data

- `IOAT_MAX_CHANNELS` is declared in the header, but allocation here is one channel object per discovered IOAT device.
- `ioat_device`: IOAT channel pointer plus allocation flag.
- `ioat_io_channel`: selected IOAT channel/device and poller.
- Global device and PCI-device queues guarded by `g_ioat_mutex` for allocation state.

## Key Control Flow

- `accel_ioat_enable_probe()` sets enable flag and adds module.
- `accel_ioat_init()` probes IOAT devices and registers IO device.
- `ioat_create_cb()` reserves a free device/channel and starts poller.
- `ioat_submit_tasks()` builds fill/copy descriptors and flushes the channel.
- Unregister callback detaches IOAT and PCI devices.

## Notes / Risks

- Supports only single-iovec copy/fill and equal source/destination lengths for copy.
- `probe_cb()` allocates a PCI tracking object before claim; claim failure leaves the allocated object in the queue until module teardown.
