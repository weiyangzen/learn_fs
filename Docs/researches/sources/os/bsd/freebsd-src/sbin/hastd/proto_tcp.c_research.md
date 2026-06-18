# File Research: sources/os/bsd/freebsd-src/sbin/hastd/proto_tcp.c

Read completely: 636 lines.

This file implements the default TCP transport backend for HAST peer communication and control/listen addresses.

Key responsibilities:
- Parses `tcp://`, `tcp4://`, `tcp6://`, bare host/IP, IPv4 host:port, and bracketed IPv6 address:port strings.
- Applies the default HAST TCP port when no port is provided.
- Creates client and server sockets, sets `TCP_NODELAY`, binds optional source addresses, enables `SO_REUSEADDR` for listeners, and listens with backlog 8.
- Connects using nonblocking mode to support explicit timeouts, then restores blocking mode.
- Supports waiting for asynchronous connect completion through `select()` and `SO_ERROR`.
- Accepts incoming connections and wraps inherited descriptors.
- Sends/receives data through `proto_common_send()`/`proto_common_recv()`.
- Matches a connected peer against a configured address by resolving the configured address and comparing only IP address bytes.
- Renders local/remote addresses with the `pjdlog` `%S` socket-address formatter.
- Registers itself as the default protocol named `tcp`.

Important interactions:
- Used for HAST peer replication connections and daemon listen/control sockets.
- Works with `proto.c` connection passing, where accepted or newly connected TCP descriptors can be wrapped in another process.

Reliability and security notes:
- Address parsing bounds host and port buffers and validates numeric port range 1-65535.
- `tcp_address_match()` ignores port and matches only address family and IP address, which is deliberate access control behavior to note.
- `tcp_accept()` stores the accepted peer address into the listener context’s sockaddr storage before allocating the work context, so listener-local address state is overwritten by the last accept.
- Descriptor passing is not supported directly by TCP send/recv; assertions require `fd == -1` and `fdp == NULL`.
