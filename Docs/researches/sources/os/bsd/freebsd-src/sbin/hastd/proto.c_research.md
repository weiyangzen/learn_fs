# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto.c

Read completely: 444 lines.

This file implements the generic transport abstraction for HAST connections. Protocol backends register themselves at constructor time, and callers use uniform client/server/send/recv/descriptor/address APIs.

Key responsibilities:
- Maintains a global queue of `struct proto` backends.
- Registers default and non-default protocols, with the default inserted last.
- Allocates typed `struct proto_conn` wrappers for client, server-listen, and server-work sides.
- Selects a backend by asking each protocol to create a client or server context for an address.
- Wraps backend connect, connect-wait, accept, send, receive, descriptor, address-match, local-address, remote-address, timeout, and close operations.
- Sends and receives already-open protocol connections by passing the backend name plus a file descriptor over another proto connection.

Important interactions:
- `proto_tcp.c` registers the default `tcp` backend.
- `proto_socketpair.c` registers `socketpair` for parent/child and descriptor-migration channels.
- `proto_common.c` provides shared send/recv helpers for socket-like backends.

Reliability notes:
- The abstraction relies heavily on backend function-pointer completeness and side assertions.
- `proto_timeout()` sets both send and receive socket timeouts on the descriptor returned by the backend.
- Connection passing requires the receiving process to have a backend with the transmitted protocol name.
