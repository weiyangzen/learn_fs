# File Research: sources/virtualization/nvme-cli/libnvme/src/nvme/no-uring.c

## Role

Build-time fallback for io_uring passthrough support when async io_uring support is disabled.

## Behavior

- `libnvme_open_uring()` returns `-ENOTSUP`.
- `libnvme_close_uring()` is a no-op.
- `__libnvme_transport_handle_open_uring()` marks `hdl->uring_state` as `LIBNVME_IO_URING_STATE_NOT_AVAILABLE` and returns `-ENOTSUP`.
- Async admin and I/O passthrough submission functions try to initialize uring if the state is unknown, then return `-ENOTSUP`.
- Reap and wait helpers return `-ENOTSUP`.

## Dependencies

Includes `errno.h`, `libnvme.h`, `private.h`, and `compiler-attributes.h`.

## Notes

The state transition to `NOT_AVAILABLE` lets higher-level code fall back to synchronous passthrough without repeatedly probing unavailable uring support.
