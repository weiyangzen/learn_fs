# sources/user-network-fs/samba/source4/lib/socket/socket.c

## Purpose

`socket.c` is the common source4 socket facade. It allocates and owns `struct socket_context`, validates state transitions, dispatches calls through `struct socket_ops`, converts between Samba `socket_address` and `tsocket_address`, and selects IPv4, IPv6, or Unix-domain backends by family name.

## Important APIs, Types, and Functions

The file exports `socket_create_with_ops()`, `socket_create()`, `socket_connect()`, `socket_connect_complete()`, `socket_listen()`, `socket_accept()`, `socket_recv()`, `socket_recvfrom()`, `socket_send()`, `socket_sendto()`, `socket_pending()`, `socket_set_option()`, address getters/converters, `socket_get_fd()`, `socket_dup()`, address constructors/copy helpers, `socket_getops_byname()`, and `socket_set_flags()`. The private `socket_destructor()` closes backend sockets unless `SOCKET_FLAG_NOCLOSE` is set.

## Control Flow

Creation allocates a talloc-owned context, initializes neutral state, calls backend `fn_init`, enables randomized short I/O when `SOCKET_TESTNONBLOCK` is set for streams, makes datagram sockets nonblocking immediately, and installs the destructor. Public operations check null pointers, socket type, and `enum socket_state` before calling the backend vtable. Send and receive optionally simulate partial nonblocking I/O, including a special encrypted path that preserves resend consistency.

## State and Persistence Behavior

State is in `struct socket_context`: type, current state, flags, fd, private backend data, ops, backend name, and address family. The facade does not persist external data, but it owns file descriptor lifetime through talloc. Address constructors allocate independent talloc-owned copies of textual addresses or `sockaddr` blobs.

## Dependencies and Integration Points

This layer depends on talloc, NTSTATUS mapping, Unix networking headers, Samba `set_blocking()`, `print_sockaddr()`, `set_sockaddr_port()`, and libtsocket conversion helpers. It integrates with `socket_ip.c`, `socket_unix.c`, async connect helpers, packet framing, and SMB client transports.

## Risks and Edge Cases

The facade trusts backend callbacks and only partially normalizes accepted contexts. `socket_address_from_sockaddr()` can return an object for an unknown family with no family string. `socket_dup()` does not restore close-on-exec. Random partial I/O can expose callers that assume full writes or reads.

## Test Signals

The local socket torture suite exercises UDP/TCP send, receive, accept, and address reporting. Additional useful signals are IPv6 and Unix-domain coverage, `SOCKET_TESTNONBLOCK=1` runs, fd ownership tests for `SOCKET_FLAG_NOCLOSE`, and `tsocket_address` conversion round trips.
