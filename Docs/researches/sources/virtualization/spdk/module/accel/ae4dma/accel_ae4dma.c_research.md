# File Research: sources/virtualization/spdk/module/accel/ae4dma/accel_ae4dma.c

## Purpose

Implements an SPDK accel backend for AMD AE4DMA hardware, currently supporting copy operations.

## Main Responsibilities

- Registers an `spdk_accel_module_if` named `"ae4dma"` when enabled.
- Probes AE4DMA PCI devices with `spdk_ae4dma_probe`.
- Claims matching PCI devices and tracks them for detach.
- Allocates per-thread IO channels from hardware queues.
- Submits SPDK copy tasks via `spdk_ae4dma_build_copy`.
- Polls AE4DMA completions with `spdk_ae4dma_process_events`.
- Flushes built descriptors after batched submissions.
- Emits JSON config entry for `ae4dma_scan_accel_module`.

## Key Data

- `AE4DMA_MAX_CHANNELS = 2`.
- `g_ae4dma_enable`, `g_ae4dma_initialized`.
- `ae4dma_device`: hardware channel pointer and available queue count.
- `ae4dma_io_channel`: selected AE4DMA channel, queue id, and poller.
- Global device and PCI-device TAILQs guarded by `g_ae4dma_mutex` for queue allocation.

## Supported Operations

- `SPDK_ACCEL_OPC_COPY` only.

## Notes / Risks

- `ae4dma_supports_opcode()` asserts if queried before initialization.
- Device queue allocation is simple first-fit across devices.
- `probe_cb()` allocates a `pci_device` before claiming; if claim fails, the allocated entry is not removed in that local path.
