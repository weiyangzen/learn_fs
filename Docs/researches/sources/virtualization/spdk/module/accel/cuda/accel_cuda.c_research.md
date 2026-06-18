# File Research: sources/virtualization/spdk/module/accel/cuda/accel_cuda.c

## Purpose

Implements an SPDK accel backend using CUDA streams and CUDA kernels for copy, fill, and XOR operations.

## Main Responsibilities

- Registers accel module `"accel_cuda"` after `cuda_scan_accel_module`.
- Verifies CUDA device availability with `cudaGetDeviceCount`.
- Creates a CUDA memory map via `cuda_utils_create_mem_map`.
- Creates per-channel CUDA streams and DMA buffers for kernel parameters/status.
- Schedules tasks onto idle streams, queues overflow tasks, and completes tasks from a poller.
- Falls back to software XOR for small XOR requests or too many sources.
- Emits JSON config for `cuda_scan_accel_module`.

## Key Data

- `ACCEL_CUDA_STREAMS_PER_CHANNEL = 4`.
- `ACCEL_CUDA_XOR_MIN_BUF_LEN = 4096`.
- `cuda_task`: SPDK task extension used in queues.
- `cuda_stream`: CUDA stream, current task, input pointer array, and status byte.
- `cuda_io_channel`: waiting/completion queues, idle stream queue, poller, per-stream buffers.

## Supported Operations

- `SPDK_ACCEL_OPC_XOR`
- `SPDK_ACCEL_OPC_FILL`
- `SPDK_ACCEL_OPC_COPY`

## Key Control Flow

- Submit functions validate task shape and call `_accel_cuda_start_request`.
- `_accel_cuda_submit_request` takes an idle stream, sets status to `-1`, launches the relevant CUDA kernel wrapper, and increments running count.
- `accel_cuda_poller` scans stream status bytes for completion, recycles streams, starts queued tasks, and completes finished SPDK accel tasks.

## Dependencies

- CUDA Runtime API.
- Kernel launch wrappers from `accel_cuda_kern.h`.
- Memory registration helper from `cuda_utils.h`.
- SPDK accel, env, thread, JSON, and XOR helpers.

## Notes / Risks

- Kernel completion is inferred from a status byte written by CUDA-side work; the `.cu` file defines the actual semantics.
- Only XOR has a software fallback; copy/fill require CUDA launch success.
- Channel creation allocates CUDA streams and SPDK DMA memory; failures clean up partially allocated resources.
