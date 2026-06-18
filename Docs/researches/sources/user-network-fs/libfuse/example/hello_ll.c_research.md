# sources/user-network-fs/libfuse/example/hello_ll.c

## Purpose

`hello_ll.c` is the minimal low-level libfuse filesystem example. It exposes inode 1 as root and inode 2 as a read-only `hello` file, plus simple xattr callback demonstrations. The source was read as a complete 297-line file.

## Important APIs, Types, and Functions

Low-level callbacks are `hello_ll_init`, `hello_ll_lookup`, `hello_ll_getattr`, `hello_ll_readdir`, `hello_ll_open`, `hello_ll_read`, `hello_ll_getxattr`, `hello_ll_setxattr`, and `hello_ll_removexattr`. Helpers include `hello_stat`, `dirbuf_add`, `reply_buf_limited`, and the manual session setup in `main`.

## Control Flow

`main` parses FUSE cmdline options, handles help/version, creates a session, installs signal handlers, mounts, daemonizes, and enters single-threaded or multi-threaded loops. Lookup maps root/name to inode 2, getattr emits fixed stat data, readdir builds a packed directory buffer, open enforces read-only access, read replies from `hello_str`, and xattr callbacks accept only hard-coded names/values.

## State and Persistence Behavior

The filesystem has no mutable storage besides process-global constants. Kernel attr and entry caches are set to one second in lookup/getattr replies.

## Dependencies and Integration Points

It depends on `fuse_lowlevel.h` and demonstrates the lower-level session API rather than `fuse_main`.

## Risks and Edge Cases

The file asserts expected inode values in read/xattr paths, so malformed internal calls abort instead of returning errors. Directory buffers are rebuilt per request and allocated with `realloc` without failure checks, acceptable for an example but not production.

## Test Signals

Mount and verify lookup/stat/readdir/read, xattr get/set/remove with accepted and rejected names, help/version paths, single-thread and multi-thread loops, and non-read-only open denial.
