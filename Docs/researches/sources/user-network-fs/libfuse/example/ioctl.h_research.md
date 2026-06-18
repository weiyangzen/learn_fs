# sources/user-network-fs/libfuse/example/ioctl.h

## Purpose

`ioctl.h` defines the shared ioctl ABI for libfuse ioctl examples and their clients. It declares restricted size ioctls and unrestricted variable-buffer read/write ioctls, plus the struct used for the latter. The source was read as a complete 49-line file.

## Important APIs, Types, and Functions

Definitions are `FIOC_GET_SIZE`, `FIOC_SET_SIZE`, `FIOC_READ`, `FIOC_WRITE`, and `struct fioc_rw_arg` with `offset`, `buf`, `size`, `prev_size`, and `new_size`.

## Control Flow

No executable flow. Kernel and FUSE ioctl handlers interpret the encoded command numbers and shared argument layout.

## State and Persistence Behavior

No state is stored. The header defines the in-memory ABI shared between server and client examples.

## Dependencies and Integration Points

It depends on `sys/types.h`, `sys/uio.h`, and `sys/ioctl.h`. It is included by `ioctl.c`, `ioctl_ll.c`, `cuse.c`, and their clients.

## Risks and Edge Cases

The unrestricted `_IO` commands intentionally do not encode size, so handlers must use retry/iovec mechanisms and are only suitable for CUSE or privileged/low-level demonstrations. ABI layout depends on native pointer and `size_t` widths, so clients and servers must be same-ABI processes.

## Test Signals

Compile all ioctl examples and clients together, verify command numbers, and run cross-command read/write/size tests on the same architecture.
