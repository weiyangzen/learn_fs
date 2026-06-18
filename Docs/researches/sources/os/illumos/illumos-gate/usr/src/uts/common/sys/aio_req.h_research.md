# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/aio_req.h

## Purpose

`aio_req.h` exposes the small asynchronous I/O request structure visible to drivers.

## Main Interface

Kernel builds define:

`struct aio_req` with:
- `aio_uio`, the `uio` for the request.
- `aio_private`, opaque driver-private data.

The header also declares `aphysio()` for asynchronous physical I/O submission and `anocancel()` as a no-cancel callback for buffers.

## Research Notes

This is the narrow driver-facing AIO contract. It deliberately hides the larger `aio_req_t` implementation details from drivers while letting physical-device and filesystem code participate in asynchronous I/O.
