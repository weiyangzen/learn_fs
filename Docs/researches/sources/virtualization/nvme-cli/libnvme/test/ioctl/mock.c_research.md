# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.c

## Role

`mock.c` implements the ioctl interception layer used by the libnvme ioctl tests. It replaces `ioctl()` for NVMe admin and I/O passthrough requests and validates each call against a preloaded sequence of `struct mock_cmd` expectations.

## Behavior

The file maintains two independent command queues: one for admin commands and one for I/O commands. Test code calls `set_mock_admin_cmds()` or `set_mock_io_cmds()` before invoking libnvme, and `end_mock_cmds()` verifies all expected calls were consumed.

The `execute_ioctl` macro validates opcode, flags, namespace ID, command dwords 2-3 and 10-15, metadata pointer content, data length, data payload for input commands, timeout, and result width. For output commands it copies synthetic bytes from `mock_cmd.out_data` into the caller-provided data buffer and writes the mocked result field.

The interposed `ioctl()` dispatches `LIBNVME_IOCTL_ADMIN_CMD`, `LIBNVME_IOCTL_ADMIN64_CMD`, `LIBNVME_IOCTL_IO_CMD`, and `LIBNVME_IOCTL_IO64_CMD`. Unknown ioctls are delegated with `dlsym(RTLD_NEXT, "ioctl")` when available, otherwise rejected with `-ENOTTY`.

The file also defines `io_uring_get_probe()` to return `0`, forcing tests away from io_uring probing and onto the ioctl path.

## Dependencies

- Uses internal `nvme/private.h` Linux passthrough command structures.
- Uses `mock.h` for expectations.
- Uses `util.h` for assertions and byte comparisons.
- Needs platform-specific ioctl signature handling via `NVME_HAVE_GLIBC_IOCTL`.

## Filesystem/Storage Relevance

This is a deterministic mock for NVMe storage ioctl ABI testing. It is central to validating libnvme command encoding without requiring a kernel NVMe device.
