# File Research: sources/virtualization/nvme-cli/libnvme/test/ioctl/mock.h

## Role

`mock.h` declares the ioctl-test expectation structure and the functions used to install and finalize mock NVMe passthrough command sequences.

## API

`struct mock_cmd` models one expected passthrough ioctl invocation. It records opcode, flags, namespace ID, command dwords, metadata, input payload, data length, timeout, output payload, result value, and ioctl return/error behavior.

`set_mock_fd()` sets the expected file descriptor. `set_mock_admin_cmds()` and `set_mock_io_cmds()` install ordered slices of expected admin and I/O commands. `end_mock_cmds()` checks that no expected commands remain unexecuted.

## Design Notes

The struct distinguishes `in_data` from `out_data`: `in_data` means the test expects libnvme to submit those bytes, while `out_data` is copied back into the caller’s buffer. `out_data_len` can override `data_len` for partial output copying.

The `result` documentation explicitly notes 64-bit result handling: if a result cannot fit in `u32`, the test must use a 64-bit ioctl path.

## Filesystem/Storage Relevance

This header defines the test contract for Linux NVMe passthrough command encoding.
