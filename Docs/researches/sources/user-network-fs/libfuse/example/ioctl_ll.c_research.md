# sources/user-network-fs/libfuse/example/ioctl_ll.c

## Purpose

`ioctl_ll.c` is a low-level FUSE ioctl example for a single in-memory `fioc` file. It demonstrates both restricted `_IOR/_IOW` size ioctls and unrestricted `_IO` read/write ioctls that require `fuse_reply_ioctl_retry`. The source was read as a complete 472-line file.

## Important APIs, Types, and Functions

Callbacks in `fioc_ll_oper` include `fioc_ll_lookup`, `fioc_ll_getattr`, `fioc_ll_readdir`, `fioc_ll_open`, `fioc_ll_read`, `fioc_ll_write`, and `fioc_ll_ioctl`. Helpers are `fioc_resize`, `fioc_expand`, `fioc_stat`, `dirbuf_add`, `reply_buf_limited`, and `fioc_do_rw`. State is `fioc_buf` and `fioc_size`.

## Control Flow

`main` manually creates a low-level session, mounts, daemonizes, and runs a single-threaded or multi-threaded loop. Lookup maps root/name to inode 2. Read/write operate on the global buffer. Ioctl rejects non-file and compat calls; restricted commands reply directly when buffers are supplied or request retry buffers otherwise; unrestricted read/write first request `fioc_rw_arg`, then user data/output buffers, then reply with iovecs.

## State and Persistence Behavior

Data is volatile memory. The program has no locking around global buffer and size, so multi-threaded runs can race.

## Dependencies and Integration Points

It depends on `fuse_lowlevel.h` and `ioctl.h`, and is paired with `ioctl_ll_client.c`.

## Risks and Edge Cases

Comments note unrestricted ioctls are blocked for regular FUSE mounts by kernel policy in many cases, so behavior differs from CUSE. Allocation failures in `FIOC_SET_SIZE` are ignored. Offset/size overflow and concurrent resizing remain example-level risks.

## Test Signals

Run restricted get/set via both clients, attempt unrestricted read/write and observe expected kernel behavior, test help/version, invalid inode paths, compat ioctl rejection, and multi-thread read/write stress.
