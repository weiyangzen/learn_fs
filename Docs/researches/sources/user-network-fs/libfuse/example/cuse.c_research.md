# sources/user-network-fs/libfuse/example/cuse.c

## Purpose

`cuse.c` is a libfuse CUSE example that implements a character device backed by a process-local resizable memory buffer. It demonstrates low-level CUSE callbacks, unrestricted ioctl retry flows, and command-line parsing for major/minor/device name. The source was read as a complete 335-line file.

## Important APIs, Types, and Functions

Important callbacks are `cusexmp_init`, `cusexmp_open`, `cusexmp_read`, `cusexmp_write`, and `cusexmp_ioctl`, registered in `cusexmp_clop`. Helpers include `cusexmp_resize`, `cusexmp_expand`, `fioc_do_rw`, `cusexmp_process_arg`, and `main`. State is `cusexmp_buf` and `cusexmp_size`.

## Control Flow

`main` parses options, requires `--name` unless showing help, builds `DEVNAME=...`, sets `CUSE_UNRESTRICTED_IOCTL`, and calls `cuse_lowlevel_main`. Reads and writes clamp/expand the global buffer. Ioctl dispatch handles restricted `FIOC_GET_SIZE`/`FIOC_SET_SIZE` and unrestricted `FIOC_READ`/`FIOC_WRITE` by using `fuse_reply_ioctl_retry` to request user buffers before replying with iovecs.

## State and Persistence Behavior

All device contents are volatile memory in a single global buffer. There is no synchronization, so multi-threaded access can race in this demonstration program.

## Dependencies and Integration Points

It depends on `cuse_lowlevel.h`, `fuse_opt.h`, and the shared `ioctl.h` contract used by client examples.

## Risks and Edge Cases

Pointer arithmetic on `void *` relies on compiler extensions. Concurrent read/write/ioctl resizing can race. `strncat` may truncate long names. Offset plus size arithmetic can overflow for extreme requests.

## Test Signals

Run as root with `cuse_client`, exercise size get/set, normal read/write, unrestricted ioctl read/write, missing `--name`, help mode, and large sparse offsets.
