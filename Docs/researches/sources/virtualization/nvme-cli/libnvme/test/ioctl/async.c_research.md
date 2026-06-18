# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/async.c

## Purpose
Tests passthrough async API behavior when io_uring support is unavailable.

## Test Coverage
- Async admin submit returns `-ENOTSUP`.
- Async I/O submit returns `-ENOTSUP`.
- Async reap returns `-ENOTSUP`.
- Synchronous admin and I/O passthrough still work through mock ioctl.
- Batched submit pattern falls back to sync execution, while `libnvme_wait_passthru()` reports unsupported without io_uring.

## Relevance
Ensures no-uring environments have predictable fallback behavior for passthrough command users.
