# sources/test-tools/fio/engines/net.c

## Purpose
Implements fio network engines `net` and, when Linux splice support is enabled, `netsplice`. It sends and receives fio I/O buffers over TCP, UDP, IPv6 variants, UNIX sockets, and vsock streams, with optional ping-pong behavior, socket tuning, multicast support, UDP sequencing, and splice/vmsplice data movement.

## Important APIs, Types, And Functions
`struct netio_data` stores listen fd, splice pipe fds, resolved socket addresses, and UDP sequence counters. `struct netio_options` stores port, protocol, listen/pingpong flags, TCP_NODELAY, TTL, window size, MSS, and multicast interface. Important functions include `fio_netio_setup()`, `fio_netio_init()`, `fio_netio_open_file()`, `fio_netio_connect()`, `fio_netio_accept()`, `fio_netio_queue()`, `fio_netio_send()`, `fio_netio_recv()`, splice helpers, UDP open/close helpers, address setup helpers, and cleanup/terminate.

## Control Flow
`setup` creates a synthetic fio file and allocates net state. `init` rejects random I/O, validates protocol/port/filename combinations, offsets the port by subjob number, and either prepares a listening socket or resolves/connects a peer address. `open_file` accepts or connects a socket, then performs UDP open handshake if needed. `queue` performs synchronous send or receive for the requested direction; ping-pong mode immediately performs the opposite direction after a completed operation. Datagram protocols are forced to one direction, while TCP/vsock can listen or connect. `netsplice` uses pipes plus splice/vmsplice for stream protocols except UDP and UNIX sockets.

## State And Persistence
Network state is process runtime only: listen fd, accepted/connected fd, pipe fds, UDP sequence counters, and peer addresses. UDP close/open control messages signal lifecycle. Sequence trailers track dropped UDP datagrams in fio stats when verify is disabled.

## Dependencies And Integration Points
Depends on POSIX sockets, optional IPv6/vsock/splice/TCP socket options, fio synthetic files, fio unidirectional pipe I/O flags, and fio termination behavior. `hostname` option writes into `td->o.filename`.

## Risks
Synchronous send/recv loops can block indefinitely through `poll_wait()`. Close notification is sent for all protocols through `sendto()` with protocol-dependent address handling. UDP open/close magic uses mixed host/network/le conversions in different paths. `fio_netio_terminate()` sends SIGTERM to `td->pid`. Multicast is IPv4-only. Port is mutated by subjob number during init, which can surprise reused option state.

## Test Signals
Test TCP client/server, UDP sender/receiver, IPv6 builds, UNIX sockets, vsock with and without support, multicast join/interface/TTL, ping-pong, close/open handshakes, UDP sequence loss accounting, socket window/MSS/TCP_NODELAY options, netsplice stream transfer, partial send/recv and EMSGSIZE busy behavior, and termination while blocked in accept/poll.
