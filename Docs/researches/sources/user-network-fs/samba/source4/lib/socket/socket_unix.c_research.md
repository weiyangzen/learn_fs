# sources/user-network-fs/samba/source4/lib/socket/socket_unix.c

## Purpose

`socket_unix.c` implements the Unix-domain socket backend for the source4 socket abstraction. It supports stream and datagram Unix sockets, path-based connect/listen/sendto, accept, byte I/O, pending-byte queries, and generic local address reporting.

## Important APIs, Types, and Functions

The exported selector is `socket_unixdom_ops()`. Backend functions include `unixdom_init()`, `unixdom_connect()`, `unixdom_connect_complete()`, `unixdom_listen()`, `unixdom_accept()`, `unixdom_recv()`, `unixdom_send()`, `unixdom_sendto()`, `unixdom_pending()`, peer/local address getters, and `unixdom_close()`.

## Control Flow

Initialization creates a `PF_UNIX` socket matching the requested type. Connect validates path length, builds `sockaddr_un`, connects, checks `SO_ERROR`, makes the fd nonblocking, and marks the client connected. Listen unlinks an existing path, binds, optionally listens for streams, makes the fd nonblocking, marks server listen, and stores the path in `private_data`. Datagram `sendto()` may retry once with a larger `SO_SNDBUF` after `EMSGSIZE`.

## State and Persistence Behavior

The backend stores the listen path as talloc-owned `private_data` but does not unlink it in `unixdom_close()`. Fd lifetime is otherwise managed by the common talloc destructor. Peer and local address getters return `LOCAL/unixdom` as a synthetic address with `port=0`.

## Dependencies and Integration Points

It depends on Unix socket APIs, Samba close-on-exec and errno-to-NTSTATUS mapping, and the common `socket_context` vtable. It is built as the internal `socket_unix` module and selected by family `"unix"`.

## Risks and Edge Cases

`unixdom_listen()` has a suspicious `my_address->sockaddr` branch that binds an uninitialized local `my_addr` instead of the supplied sockaddr. Stale socket path cleanup only happens before bind, not on close. Path length checks use `strlen()+1 > sizeof(sun_path)` but abstract namespace sockets are not represented.

## Test Signals

Useful tests should cover stream connect/listen/accept, datagram sendto, long path rejection, cleanup of preexisting socket paths, supplied `sockaddr_un` inputs, and close behavior around stale filesystem socket nodes.
