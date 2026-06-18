# sources/user-network-fs/libfuse/example/hello_ll_uds.c

## Purpose

`hello_ll_uds.c` adapts the low-level hello filesystem to custom FUSE I/O over a Unix domain stream socket. It demonstrates `fuse_session_custom_io` callbacks for reading, writing, and splice sending FUSE packets outside the normal `/dev/fuse` file descriptor path. The source was read as a complete 367-line file.

## Important APIs, Types, and Functions

Filesystem callbacks mirror `hello_ll.c`: lookup/getattr/readdir/open/read. Custom I/O helpers are `create_socket`, `stream_writev`, `readall`, `stream_read`, and `stream_splice_send`, supplied through `struct fuse_custom_io`. `main` creates a session and binds it to a connected socket.

## Control Flow

The program parses help/version, creates a low-level session, installs signal handlers, waits for a client connection on `/tmp/libfuse-hello-ll.sock`, registers custom I/O, and runs `fuse_session_loop`. `stream_read` first reads a `fuse_in_header`, uses its `len` to read the rest of the packet, and `stream_writev` drains an iovec sequence with repeated `writev` calls.

## State and Persistence Behavior

Filesystem data is static. Runtime socket filesystem state is the socket path under `/tmp`; the program removes an old socket entry before binding but does not explicitly close all descriptors on every failure path.

## Dependencies and Integration Points

It depends on low-level libfuse, `fuse_kernel.h`, Unix sockets, `readv/writev` style I/O, and `splice`. It is built on non-BSD platforms in the example Meson file.

## Risks and Edge Cases

Custom stream framing is sensitive to partial reads/writes and malformed packet lengths. `create_socket` can leak the listening socket on later errors. The socket path is fixed and global. `stream_writev` mutates the caller-provided iovec entries while draining them.

## Test Signals

Run with a custom client that speaks FUSE packets over the socket, test partial packet reads, disconnects, overly large packet lengths, stale socket removal, and normal hello lookup/read behavior.
