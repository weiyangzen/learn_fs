# File Research: sources/os/bsd/netbsd-src/lib/libisns/isns_socketio.c

Provides a thin socket abstraction for libisns. `isns_socket_create/connect/close` either call WEPE wrapper functions when `HAVE_WEPE` is set or normal `socket(2)`, `connect(2)`, and `close(2)` otherwise.

Read/write vector operations delegate to `isns_file_writev()` and `isns_file_readv()`, making socket I/O share file-vector retry behavior from the broader library.

This module intentionally contains no protocol logic; it exists as a portability seam for socket descriptors.
