# sources/user-network-fs/libfuse/example/ioctl_ll_client.c

## Purpose

`ioctl_ll_client.c` is the richer client for `ioctl_ll.c`. It can issue restricted size get/set commands and unrestricted read/write commands using `struct fioc_rw_arg`. The source was read as a complete 176-line file.

## Important APIs, Types, and Functions

Helpers are `do_get_size`, `do_set_size`, `do_read`, and `do_write`, all called from `main`. They invoke `FIOC_GET_SIZE`, `FIOC_SET_SIZE`, `FIOC_READ`, and `FIOC_WRITE`.

## Control Flow

`main` expects `<command> <fioc_file> [args]`, opens the file, validates command-specific arity, calls the helper, prints results including previous/new sizes for unrestricted commands, and closes the descriptor.

## State and Persistence Behavior

The client owns temporary buffers only. Writes affect the mounted example's volatile memory.

## Dependencies and Integration Points

It depends on POSIX file/ioctl APIs and the shared `ioctl.h` ABI. It tests the low-level and, for restricted commands, compatible CUSE/high-level examples.

## Risks and Edge Cases

Numeric parsing uses `strtoul`/`strtol` without end-pointer validation. Unrestricted ioctls may fail with `EIO` on normal FUSE mounts due to kernel policy, which is expected by the example comments. Read output treats data as a string by appending NUL.

## Test Signals

Run every command, invalid arity, invalid command, invalid numeric input, unrestricted ioctl failure modes on regular FUSE, and successful unrestricted operations where supported.
