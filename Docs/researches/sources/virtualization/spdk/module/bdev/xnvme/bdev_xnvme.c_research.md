# File Research: sources/virtualization/spdk/module/bdev/xnvme/bdev_xnvme.c

## Purpose
Implements an SPDK bdev backed by libxnvme.

## State
- `struct bdev_xnvme`: SPDK bdev, filename, selected async I/O mechanism, xNVMe device, namespace ID, conserve-CPU flag.
- `struct bdev_xnvme_io_channel`: one xNVMe queue plus SPDK poller.
- `struct bdev_xnvme_task`: per-I/O context linking completion back to channel.

## Lifecycle
`create_xnvme_bdev()` configures xNVMe options, opens the device, gets namespace geometry, validates block size and total size, fills bdev geometry, configures unmap/write-zeroes limits for NVM command set, registers I/O device and bdev, then links it globally for config JSON.

`delete_xnvme_bdev()` unregisters by name. Destruct unregisters the I/O device, removes the bdev from the global list, closes the xNVMe device, and frees strings/state.

## I/O Path
Supports read and write for all mechanisms. Supports write zeroes and unmap only when `io_mechanism == "io_uring_cmd"` and the device command-set identifier is NVM.

Read/write/unmap acquire aligned bdev buffers; write zeroes submits directly. `_xnvme_submit_request()` fills NVMe command fields and calls `xnvme_cmd_passv()`. Queue-full/resource errors map to SPDK `NOMEM`; other submission errors fail the I/O.

Completions are polled with `xnvme_queue_poke()`. `bdev_xnvme_cmd_cb()` checks xNVMe completion status, completes the SPDK bdev I/O, and returns the command context to the queue.

## Dependencies And Risks
Depends on libxnvme command and queue APIs plus SPDK bdev/thread/poller support. Queue depth is fixed at 512. `bdev_xnvme_get_buf_cb()` contains an unusual failure path that obtains and immediately returns a command context even though no submission occurred.
