# sources/user-network-fs/samba/source4/lib/socket/socket.h

## Purpose

`socket.h` declares the source4 socket abstraction shared by socket backends, async connect helpers, packet streams, and callers. It defines the public data model for socket types, socket addresses, backend vtables, state values, flags, and exported helper APIs.

## Important APIs, Types, and Functions

Core types are `enum socket_type`, `struct socket_address`, `struct socket_ops`, `enum socket_state`, and `struct socket_context`. Flags include `SOCKET_FLAG_PEEK`, `SOCKET_FLAG_TESTNONBLOCK`, `SOCKET_FLAG_ENCRYPT`, and `SOCKET_FLAG_NOCLOSE`. The header declares synchronous operations, address conversion/copy functions, access checking, async connect APIs, multi-address connect APIs, `set_socket_options()`, `socket_set_flags()`, and `socket_tevent_fd_close_fn()`.

## Control Flow

The header has no runtime flow. Its contracts define which state transitions implementations must support: undefined to client connected, server listen to accepted server connected, and starttls/error states used by higher layers. `struct socket_ops` is the vtable dispatch point used by `socket.c`.

## State and Persistence Behavior

The state contract is explicit in `struct socket_context`; ownership is talloc-centered, with fd cleanup controlled by flags and backend close functions. `struct socket_address` may represent either a textual family/address/port tuple or an already-materialized `sockaddr` and length.

## Dependencies and Integration Points

The header forward-declares tevent, resolve, composite, and tsocket types while relying on Samba base types from including translation units. It is included by socket backends, stream packet code, TLS declarations, SMB client socket code, and tests.

## Risks and Edge Cases

The public structs expose implementation details, so ABI and source compatibility are fragile. Callers can mutate state, flags, and fd directly. `SOCKET_FLAG_ENCRYPT` has subtle interaction with test nonblocking behavior, and address objects with both textual and `sockaddr` fields require callers to understand precedence.

## Test Signals

Compile coverage across socket, stream, TLS, and libcli users is the main header signal. Behavioral tests should verify that all backends implement every required vtable operation for both stream and datagram where advertised.
